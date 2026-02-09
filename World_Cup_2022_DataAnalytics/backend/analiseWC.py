from statsbombpy import sb
import pandas as pd
import warnings

# Ignora avisos chatos da biblioteca
warnings.filterwarnings("ignore")

def obter_dados_partida(match_id):
    """
    Busca dados reais da StatsBomb.
    Se match_id for 0, pega a FINAL da Copa (Argentina x França).
    """
    
    print("⏳ Baixando dados da StatsBomb... (isso pode demorar uns segundos)")
    
    # ID da Final da Copa 2022 é 3869685
    # Se for outro jogo, teria que buscar o ID antes
    MATCH_ID_REAL = 3869685 
    
    # 1. Busca os eventos direto da API
    # fmt="dataframe" já devolve um Pandas DataFrame pronto!
    events = sb.events(match_id=MATCH_ID_REAL)

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
            
            # Conversão para porcentagem (CSS)
            # Invertemos o Y porque no HTML o 0 é no topo, no futebol às vezes varia
            x_percent = (x_original / 120) * 100
            y_percent = (y_original / 80) * 100 
            
            lista_acoes.append({
                "x": round(x_percent, 2),
                "y": round(y_percent, 2),
                "jogador": row['player'],
                "tipo": row['type'],
                "time": row['team']
            })

    # 4. Cálculo do Usage Rate (Simplificado para Volume de Jogo)
    # Quem tocou mais na bola?
    contagem = df_filtrado['player'].value_counts(normalize=True).head(10) * 100
    
    lista_usage = []
    for jogador, porcentagem in contagem.items():
        lista_usage.append({
            "jogador": jogador,
            "usage_rate": round(porcentagem, 2)
        })

    print(f"✅ Sucesso! {len(lista_acoes)} eventos processados.")

    return {
        "usage_rate": lista_usage,
        "mapa_acoes": lista_acoes # Mandamos apenas os primeiros 500 para não travar o navegador se for muito grande
    }