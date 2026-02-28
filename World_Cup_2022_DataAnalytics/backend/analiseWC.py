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

def treinar_modelo_global(df_completo):
    """
    Treina um único modelo XGBoost usando os dados de TODAS as partidas.
    """
    df_ml = df_completo.copy()
    
    # Mapeamento manual de tipos para garantir consistência em todos os jogos
    tipo_map = {'Pass': 1, 'Shot': 2, 'Carry': 3, 'Dribble': 4}
    df_ml['type_id'] = df_ml['type'].map(tipo_map).fillna(0)
    
    # Extrai coordenadas de forma segura
    df_ml['loc_x'] = df_ml['location'].apply(lambda x: float(x[0]) if isinstance(x, list) else 0.0)
    df_ml['loc_y'] = df_ml['location'].apply(lambda x: float(x[1]) if isinstance(x, list) else 0.0)
    
    features = ['loc_x', 'loc_y', 'type_id', 'period', 'minute']
    X = df_ml[features]

    # Target: Ocorreu gol nos próximos 10 lances?
    lookahead = 10
    y = np.zeros(len(df_ml))
    goal_indices = df_ml[df_ml['shot_outcome'] == 'Goal'].index
    
    for goal_idx in goal_indices:
        start = max(0, goal_idx - lookahead)
        y[start:goal_idx] = 1
        
    # Treina o modelo "Mestre"
    model = xgb.XGBClassifier(
        n_estimators=100, 
        max_depth=4, 
        learning_rate=0.1, 
        eval_metric='logloss'
    )
    model.fit(X, y)
    
    return model

def processar_partida_com_modelo(events, modelo_global):
    """
    Recebe os eventos de 1 partida e usa o modelo Global para calcular o VAEP.
    """
    try:
        # 1. Prepara as features iguais ao modelo global
        df_ml = events.copy()
        tipo_map = {'Pass': 1, 'Shot': 2, 'Carry': 3, 'Dribble': 4}
        df_ml['type_id'] = df_ml['type'].map(tipo_map).fillna(0)
        df_ml['loc_x'] = df_ml['location'].apply(lambda x: float(x[0]) if isinstance(x, list) else 0.0)
        df_ml['loc_y'] = df_ml['location'].apply(lambda x: float(x[1]) if isinstance(x, list) else 0.0)
        
        X_pred = df_ml[['loc_x', 'loc_y', 'type_id', 'period', 'minute']]

        # 2. Preve o perigo usando a "sabedoria" de todos os jogos
        events['vaep_value'] = modelo_global.predict_proba(X_pred)[:, 1]

        mask = events['type'].isin(['Pass', 'Shot', 'Carry', 'Dribble'])
        df_filtrado = events[mask].copy()

        lista_acoes = []
        stats_dict = {} 

        for index, row in df_filtrado.iterrows():
            if isinstance(row['location'], list) and len(row['location']) == 2:
                x_original = row['location'][0]
                y_original = row['location'][1]
                
                is_goal = True if row['type'] == 'Shot' and str(row['shot_outcome']) == 'Goal' else False
                
                pct_y = (y_original / 80) * 100
                css_left = 4 + (pct_y * 0.92)

                pct_x = (x_original / 120) * 100
                css_bottom = 4 + (pct_x * 0.92)

                if is_goal:
                    css_left += random.uniform(-1, 1)
                    css_bottom += random.uniform(-1, 1)

                lista_acoes.append({
                    "left": round(css_left, 2),
                    "bottom": round(css_bottom, 2),
                    "jogador": str(row['player']),
                    "tipo": str(row['type']),
                    "time": str(row['team']),
                    "is_goal": is_goal
                })

            player = str(row['player'])
            if player not in stats_dict:
                stats_dict[player] = {'vaep_total': 0, 'acoes': 0}
            stats_dict[player]['vaep_total'] += row['vaep_value']
            stats_dict[player]['acoes'] += 1

        total_acoes_jogo = len(df_filtrado)
        scatter_data = []
        for player, dados in stats_dict.items():
            usage = (dados['acoes'] / total_acoes_jogo) * 100
            if usage > 0.5:
                scatter_data.append({
                    "x": round(usage, 2),
                    "y": round(dados['vaep_total'], 2),
                    "jogador": player
                })

                
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
        
        contagem = df_filtrado['player'].value_counts(normalize=True).head(10) * 100
        lista_usage = [{"jogador": str(j), "usage_rate": round(float(p), 2)} for j, p in contagem.items()]

        return {
            "usage_rate": lista_usage,
            "mapa_acoes": lista_acoes,
            "scatter_data": scatter_data,
            "todos_jogadores": todos_jogadores,
            "tabela_stats": [] 
        }

    except Exception as e:
        print(f"❌ ERRO: {e}")
        return {"erro": str(e)}