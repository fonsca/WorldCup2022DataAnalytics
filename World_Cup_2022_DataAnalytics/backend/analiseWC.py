from statsbombpy import sb
import pandas as pd
import numpy as np
import xgboost as xgb # <--- O ML entra aqui
from sklearn.preprocessing import LabelEncoder
import random
import warnings

warnings.filterwarnings("ignore")

def listar_partidas():
    try:
        df_matches = sb.matches(competition_id=43, season_id=106)
        lista_jogos = []
        for index, row in df_matches.iterrows():
            label = f"{row['home_team']} ({row['home_score']}) x ({row['away_score']}) {row['away_team']}"
            lista_jogos.append({
                "match_id": row['match_id'],
                "descricao": label,
                "fase": row['competition_stage']
            })
        return lista_jogos
    except:
        return []

def calcular_vaep_simplificado(events):
    """
    Função ML para calcular o valor de cada ação.
    Treina um XGBoost para prever a probabilidade de gol nos próximos 10 eventos.
    """
    # 1. Feature Engineering (Transformar dados em números para o Modelo)
    df_ml = events.copy()
    
    # Codifica o Tipo de Ação (Pass, Shot, Dribble...) para números
    le = LabelEncoder()
    df_ml['type_id'] = le.fit_transform(df_ml['type'])
    
    # Extrai coordenadas (Preenche vazios com 0)
    df_ml['loc_x'] = df_ml['location'].apply(lambda x: x[0] if isinstance(x, list) else 0)
    df_ml['loc_y'] = df_ml['location'].apply(lambda x: x[1] if isinstance(x, list) else 0)
    
    # Features que o modelo vai usar
    features = ['loc_x', 'loc_y', 'type_id', 'period', 'minute']
    X = df_ml[features]

    # 2. Criar o Label (Target): Aconteceu um gol nos próximos 10 lances?
    # Isso ensina o modelo o que é uma jogada perigosa.
    lookahead = 10
    y = np.zeros(len(df_ml))
    
    # Onde ocorreram gols?
    goal_indices = df_ml[df_ml['shot_outcome'] == 'Goal'].index
    
    for goal_idx in goal_indices:
        # Marca os 10 eventos anteriores como "levou a gol" (1)
        start = max(0, goal_idx - lookahead)
        y[start:goal_idx] = 1
        
    # 3. Treinar o Modelo XGBoost
    model = xgb.XGBClassifier(
        n_estimators=50,      # Rápido para não travar o site
        max_depth=3,          # Evita overfitting
        learning_rate=0.1,
        eval_metric='logloss'
    )
    model.fit(X, y)
    
    # 4. Prever Probabilidades (O VAEP Simplificado)
    # A probabilidade da jogada resultar em gol é o seu "valor ofensivo"
    probs = model.predict_proba(X)[:, 1] # Pega a probabilidade da classe 1 (Gol)
    
    return probs

def obter_dados_partida(match_id):
    try:
        # Busca dados reais da StatsBomb.
        # Se match_id for 0, pega a FINAL da Copa (Argentina x França).
        match_id_real = 3869685 if str(match_id) == "0" else int(match_id)
        print(f"⏳ Processando partida {match_id_real} com ML...")
        
        # Busca os eventos direto da API
        # fmt="dataframe" já devolve um Pandas DataFrame pronto!
        events = sb.events(match_id=match_id_real)

        # --- FILTRO: Remover Disputa de Pênaltis ---
        # A StatsBomb divide o jogo em períodos: 
        # 1 (1º Tempo), 2 (2º Tempo), 3 (Prorrogação 1), 4 (Prorrogação 2), 5 (Pênaltis).
        # Vamos pegar apenas até o período 4 para ver o 3x3 excluindo a disputa de pênaltis.
        events = events[events['period'] <= 4]

        # --- APLICAÇÃO DO MACHINE LEARNING ---
        # Calcula o valor de cada linha do dataframe
        events['vaep_value'] = calcular_vaep_simplificado(events)

        # Filtra para visualização
        mask = events['type'].isin(['Pass', 'Shot', 'Carry', 'Dribble'])
        df_filtrado = events[mask].copy()

        # --- PREPARA MAPA E TABELA ---
        lista_acoes = []
        stats_dict = {} # Dicionário para agregar VAEP por jogador

        for index, row in df_filtrado.iterrows():
            # (Código de coordenadas igual ao anterior)
            if isinstance(row['location'], list) and len(row['location']) == 2:
                x = row['location'][0]
                y = row['location'][1]
                is_goal = True if row['type'] == 'Shot' and str(row['shot_outcome']) == 'Goal' else False
                # --- CALIBRAÇÃO DE COORDENADAS ---
                
                # 1. EIXO Y (Largura): 0 a 80
                # Removemos a inversão (80 - y). Usamos direto.
                # Multiplicamos por 0.92 para encolher um pouco (margem da imagem)
                # Adicionamos +4 para centralizar (Padding esquerdo)
                pct_y = (y / 80) * 100
                css_left = 4 + (pct_y * 0.92)

                # 2. EIXO X (Comprimento): 0 a 120
                # Mesma lógica de encolhimento para não sair nas linhas de fundo
                pct_x = (x / 120) * 100
                css_bottom = 4 + (pct_x * 0.92)

                # Jitter
                if is_goal:
                    css_left += random.uniform(-1, 1)
                    css_bottom += random.uniform(-1, 1)

                lista_acoes.append({
                    "left": round(css_left, 2),
                    "bottom": round(css_bottom, 2),
                    "jogador": str(row['player']),
                    "tipo": str(row['type']),
                    "time": str(row['team']),
                    "is_goal": is_goal # Enviando para o JS saber se pinta de amarelo
                })

            # --- AGREGAÇÃO DE VAEP ---
            player = str(row['player'])
            if player not in stats_dict:
                stats_dict[player] = {'vaep_total': 0, 'acoes': 0}
            
            stats_dict[player]['vaep_total'] += row['vaep_value']
            stats_dict[player]['acoes'] += 1

        # --- 2. DADOS PARA O GRÁFICO SCATTER (VAEP x USAGE) ---
        total_acoes_jogo = len(df_filtrado)
        scatter_data = []
        
        for player, dados in stats_dict.items():
            # Usage Rate = (Ações do Jogador / Total Ações do Jogo) * 100
            usage = (dados['acoes'] / total_acoes_jogo) * 100
            
            # Só queremos jogadores com participação relevante (> 0.5% usage)
            if usage > 0.5:
                scatter_data.append({
                    "x": round(usage, 2),         # Eixo X: Participação
                    "y": round(dados['vaep_total'], 2), # Eixo Y: Perigo Criado (VAEP)
                    "jogador": player
                })

        # --- 3. DADOS PARA TABELA E SELETORES ---
        stats_df = pd.crosstab(df_filtrado['player'], df_filtrado['type'])
        if 'Pass' not in stats_df.columns: stats_df['Pass'] = 0
        if 'Shot' not in stats_df.columns: stats_df['Shot'] = 0
        tabela_stats = []
        for jogador in stats_df.index:
            tabela_stats.append({
                "nome": jogador,
                "passes": int(stats_df.loc[jogador, 'Pass']),
                "chutes": int(stats_df.loc[jogador, 'Shot']),
                "total": int(stats_df.loc[jogador, 'Pass'] + stats_df.loc[jogador, 'Shot'])
            })
        
        todos_jogadores = sorted(df_filtrado['player'].unique().tolist())
        
        # Usage Rate Simples para o gráfico de barras antigo
        contagem = df_filtrado['player'].value_counts(normalize=True).head(10) * 100
        lista_usage = [{"jogador": str(j), "usage_rate": round(float(p), 2)} for j, p in contagem.items()]

        return {
            "usage_rate": lista_usage,
            "mapa_acoes": lista_acoes,
            "scatter_data": scatter_data, # <--- NOVO DADO
            "todos_jogadores": todos_jogadores,
            "tabela_stats": tabela_stats
        }

    except Exception as e:
        print(f"❌ ERRO: {e}")
        return {"erro": str(e)}