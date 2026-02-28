import json
import os
import pandas as pd
from tqdm import tqdm # Barra de progresso visual
from statsbombpy import sb
from analiseWC import listar_partidas, treinar_modelo_global, processar_partida_com_modelo

# Define a pasta onde os JSONs serão salvos (sua pasta frontend)
PASTA_DESTINO = '../frontend/dados_json'

# Cria a pasta se ela não existir
if not os.path.exists(PASTA_DESTINO):
    os.makedirs(PASTA_DESTINO)

print(" Passo 1/2 - Iniciando a extração de dados da Copa do Mundo 2022...")

# 1. Baixa e salva a lista de jogos
jogos = listar_partidas()
with open(os.path.join(PASTA_DESTINO, 'lista_jogos.json'), 'w', encoding='utf-8') as f:
    json.dump(jogos, f, ensure_ascii=False, indent=4)

print(" Passo 2/4 - Baixando dados de TODAS as partidas para memória...")
todos_eventos = {}
df_lista_treino = []

for jogo in tqdm(jogos, desc="Download API StatsBomb"):
    match_id = jogo['match_id']
    events = sb.events(match_id=match_id)
    events = events[events['period'] <= 4] # Remove pênaltis
    
    todos_eventos[match_id] = events
    df_lista_treino.append(events)

print("\n Passo 3/4 - Treinando o Modelo Global de Machine Learning...")
# Junta as 64 partidas em um único Super DataFrame
df_completo = pd.concat(df_lista_treino, ignore_index=True)
modelo_global = treinar_modelo_global(df_completo)

print("\n Passo 4/4 - Calculando o VAEP e Gerando os arquivos JSON estáticos...")
for match_id, events in tqdm(todos_eventos.items(), desc="Criando Dashboard"):
    dados_json = processar_partida_com_modelo(events, modelo_global)
    caminho_partida = os.path.join(PASTA_DESTINO, f'partida_{match_id}.json')
    with open(caminho_partida, 'w', encoding='utf-8') as f:
        json.dump(dados_json, f, ensure_ascii=False, indent=4)

print("\n🎉 SUCESSO! Todos os JSONs gerados. A inteligência do seu projeto agora é Global!")