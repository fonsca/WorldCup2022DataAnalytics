import json
import os
from tqdm import tqdm # Barra de progresso visual
from analiseWC import listar_partidas, obter_dados_partida

# Define a pasta onde os JSONs serão salvos (sua pasta frontend)
PASTA_DESTINO = '../frontend/dados_json'

# Cria a pasta se ela não existir
if not os.path.exists(PASTA_DESTINO):
    os.makedirs(PASTA_DESTINO)

print("Iniciando a extração de dados da Copa do Mundo 2022...")

# 1. Baixa e salva a lista de jogos
jogos = listar_partidas()
caminho_lista = os.path.join(PASTA_DESTINO, 'lista_jogos.json')

with open(caminho_lista, 'w', encoding='utf-8') as f:
    json.dump(jogos, f, ensure_ascii=False, indent=4)
print(f"Lista de {len(jogos)} jogos salva com sucesso!")

# 2. Baixa e salva os dados de CADA jogo
print("Iniciando processamento de Machine Learning para cada partida...")
for jogo in tqdm(jogos, desc="Processando Partidas"):
    match_id = jogo['match_id']
    dados_partida = obter_dados_partida(match_id)
    
    caminho_partida = os.path.join(PASTA_DESTINO, f'partida_{match_id}.json')
    with open(caminho_partida, 'w', encoding='utf-8') as f:
        json.dump(dados_partida, f, ensure_ascii=False, indent=4)

print("Todos os arquivos JSON foram gerados com sucesso na pasta frontend/dados_json!")