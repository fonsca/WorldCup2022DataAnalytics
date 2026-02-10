from statsbombpy import sb
import pandas as pd
import random
import warnings

# Ignora avisos chatos da biblioteca
warnings.filterwarnings("ignore")

def listar_partidas():
    """Baixa a lista de todos os jogos da Copa 2022"""
    try:
        # 43 = Copa do Mundo, 106 = Temporada 2022
        df_matches = sb.matches(competition_id=43, season_id=106)
        
        # Lista para o Frontend
        lista_jogos = []
        for index, row in df_matches.iterrows():
            # Formata: "Argentina (3) vs (3) França"
            label = f"{row['home_team']} ({row['home_score']}) x ({row['away_score']}) {row['away_team']}"
            
            lista_jogos.append({
                "match_id": row['match_id'],
                "descricao": label,
                "fase": row['competition_stage'] # Para agrupar depois
            })
            
        # Ordena alfabeticamente ou por data (opcional)
        return lista_jogos
    except Exception as e:
        return []

def obter_dados_partida(match_id):
    try:
        """
        Busca dados reais da StatsBomb.
        Se match_id for 0, pega a FINAL da Copa (Argentina x França).

        """
        
        MATCH_ID_REAL = 3869685 if str(match_id) == "0" else int(match_id)
        
        print(f"⏳ Baixando partida ID: {MATCH_ID_REAL}...")
        
        # 1. Busca os eventos direto da API
        # fmt="dataframe" já devolve um Pandas DataFrame pronto!
        events = sb.events(match_id=MATCH_ID_REAL)

        # --- FILTRO: Remover Disputa de Pênaltis ---
        # A StatsBomb divide o jogo em períodos: 
        # 1 (1º Tempo), 2 (2º Tempo), 3 (Prorrogação 1), 4 (Prorrogação 2), 5 (Pênaltis).
        # Vamos pegar apenas até o período 4 para ver o 3x3 excluindo a disputa de pênaltis.
        events = events[events['period'] <= 4]

        # 2. Filtragem Básica
        # Vamos pegar apenas Passes e Chutes para o mapa não ficar ilegível
        mask = events['type'].isin(['Pass', 'Shot'])
        df_filtrado = events[mask].copy()

        # 3. Tratamento de Coordenadas
        # A coluna 'location' vem como uma lista [x, y]. Precisamos separar.
        # O campo da StatsBomb é 120x80. O HTML é 100% x 100%.
        
        lista_acoes = []
        
        for index, row in df_filtrado.iterrows():
            # Verifica se tem localização (alguns eventos não têm)
            if isinstance(row['location'], list) and len(row['location']) == 2:
                x_original = row['location'][0]
                y_original = row['location'][1]
                
# --- LÓGICA DE GOL ---
                # A coluna 'shot_outcome' diz se foi Goal, Saved, Off T, etc.
                # Se não for chute, esse valor é NaN (nulo), então tratamos isso.
                is_goal = False
                if row['type'] == 'Shot' and str(row['shot_outcome']) == 'Goal':
                    is_goal = True

                # --- LÓGICA DE CAMPO VERTICAL (PORTRAIT) ---
                # StatsBomb: X (0-120) é o comprimento, Y (0-80) é a largura.
                # Para vertical: X vira nossa altura (bottom), Y vira nossa largura (left).
                
                # Invertemos o Y (80 - y) para espelhar corretamente a esquerda/direita
                y_invertido = 80 - y_original 
                
                css_left = (y_invertido / 80) * 100
                css_bottom = (x_original / 120) * 100

                # --- TRUQUE DO JITTER (Anti-Sobreposição) ---
                # Se for GOL, adicionamos um pequeno desvio aleatório
                # para que os pênaltis não fiquem empilhados.
                if is_goal:
                    offset_x = random.uniform(-2, 2) # Desvia um pouquinho para os lados
                    offset_y = random.uniform(-2, 2) # Desvia um pouquinho para cima/baixo
                    css_left += offset_x
                    css_bottom += offset_y

                lista_acoes.append({
                    "left": round(css_left, 2),
                    "bottom": round(css_bottom, 2),
                    "jogador": str(row['player']),
                    "tipo": str(row['type']),
                    "time": str(row['team']),
                    "is_goal": is_goal  # Enviando para o JS saber se pinta de amarelo
                })

        # --- 4. PREPARAR DADOS DA TABELA ---
        # Agrupa por Nome e Tipo de Ação e conta
        stats_df = pd.crosstab(df_filtrado['player'], df_filtrado['type'])
        if 'Pass' not in stats_df.columns: stats_df['Pass'] = 0
        if 'Shot' not in stats_df.columns: stats_df['Shot'] = 0

        tabela_stats = []
        # Itera sobre os jogadores para criar o JSON
        for jogador in stats_df.index:
            tabela_stats.append({
                "nome": jogador,
                "passes": int(stats_df.loc[jogador, 'Pass']),
                "chutes": int(stats_df.loc[jogador, 'Shot']),
                "total": int(stats_df.loc[jogador, 'Pass'] + stats_df.loc[jogador, 'Shot'])
            })
        
        # Ordena quem tem mais ações primeiro
        tabela_stats = sorted(tabela_stats, key=lambda k: k['total'], reverse=True)

        # --- 5. Usage Rate (Mantido para o gráfico) ---
        contagem = df_filtrado['player'].value_counts(normalize=True).head(10) * 100
        lista_usage = [{"jogador": j, "usage_rate": round(float(p), 2)} for j, p in contagem.items()]

        # Pega todos os nomes únicos que estão no DataFrame e ordena alfabeticamente
        todos_jogadores = sorted(df_filtrado['player'].unique().tolist())

        print(f"✅ Sucesso! {len(lista_acoes)} ações processadas.")

        return {
            "usage_rate": lista_usage,      # Vai para o Gráfico
            "mapa_acoes": lista_acoes,      # Vai para o Mapa
            "tabela_stats": tabela_stats,   # Vai para a Tabela
            "todos_jogadores": todos_jogadores # Vai para o Select
        }
    
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return {"erro": str(e)}