# World Cup 2022 Analytics: End-to-End Data Science & Global ML

> **Uma aplicação completa de Data Science que extrai dados brutos da Copa do Mundo, treina um modelo Global de Machine Learning (XGBoost) com mais de 200 mil eventos para calcular o VAEP (Valuing Actions by Estimating Probabilities) e serve os resultados em um Dashboard interativo com arquitetura Serverless.**

## Sobre o Projeto

Este projeto simula o fluxo completo de um **Data Scientist / Data Engineer**, indo da extração de dados via API até a implantação na nuvem. O grande diferencial desta aplicação é a sua inteligência e arquitetura:

* **Inteligência (Global ML):** Em vez de analisar partidas isoladas, o pipeline junta todos os 64 jogos do torneio, aprendendo os padrões reais do esporte através de um modelo XGBoost treinado com o dataset completo.
* **Performance (Serverless):** O processamento pesado e as predições do ML são feitos em *batch* (lote) localmente. Os resultados são exportados como arquivos JSON estáticos, permitindo que o frontend seja hospedado de forma gratuita, à prova de falhas e super rápida via GitHub Pages.

---

## Screenshots

| Mapa Geral (Todos) | Filtro por Jogador | Análise de Eficiência (ML) |
|:---:|:---:|:---:|
| <img src="World_Cup_2022_DataAnalytics\data\TodosJogadores.png" width="300"> | <img src="World_Cup_2022_DataAnalytics\data\MapaFiltrado.png" width="300"> | <img src="World_Cup_2022_DataAnalytics\data\URxVAEP.png" width="300"> |
| *Visão tática global (Passes e Chutes)* | *Ações individuais filtradas* | *Clusterização Usage x VAEP* |

---

## Arquitetura e Decisões Técnicas

### 1. O Problema das Estatísticas Tradicionais
Um passe no meio de campo não tem o mesmo peso que um passe na pequena área, mas estatísticas comuns tratam ambos como "1 passe". Para medir o impacto real dos jogadores, implementei o **VAEP** — um modelo de Valoração de Ações.

### 2. Machine Learning: O Modelo Global (XGBoost)
* **Prevenção de Overfitting:** Inicialmente, treinar um modelo por partida gerava distorções (ex: uma partida 0x0 quebrava o algoritmo logístico). A solução foi agregar todas as 64 partidas (gerando mais de 200.000 eventos táticos).
* **Treinamento:** Um classificador `XGBClassifier` foi treinado para responder: *"Dadas as coordenadas (X, Y) e o tipo da ação, essa jogada resultou em gol nos próximos 10 lances em todo o campeonato?"*.
* **Resultado:** O modelo aprendeu os padrões reais de perigo do esporte. O dashboard permite identificar "playmakers" ocultos: jogadores que não finalizam, mas são o motor de criação do time (Quadrante Superior Direito do Gráfico de Dispersão).

### 3. Engenharia de Dados e Serverless
* **ETL em Lote:** O script `gerar_json.py` atua como um pipeline ETL. Ele extrai dados da API StatsBomb, transforma as coordenadas, aplica o modelo preditivo e carrega (Load) os resultados como 65 arquivos JSON.
* **CI/CD com GitHub Actions:** Um workflow automatizado escuta os *commits* na branch principal e faz o deploy apenas da pasta do Frontend para o GitHub Pages. Sem servidores rodando 24/7, garantindo zero custo e máxima escalabilidade.

---

## Tecnologias e Ferramentas

### Data & Machine Learning (Python)
* **StatsBombPy:** Extração de dados oficiais da Copa 2022.
* **Pandas & NumPy:** Manipulação de dados, agregações e Feature Engineering.
* **XGBoost & Scikit-Learn:** Algoritmo de Gradient Boosting e pré-processamento (Label Encoding) para o cálculo preditivo do VAEP.
* **tqdm:** Monitoramento de progresso de loops em lote.

### Frontend & Deploy
* **JavaScript (Vanilla) & API Fetch:** Consumo assíncrono dos JSONs estáticos.
* **Chart.js:** Renderização de gráficos de dispersão e barras.
* **GitHub Actions & Pages:** Automação de deploy e hospedagem Serverless.

---

## Como Rodar o Projeto (Localmente)

Se você quiser reproduzir o treinamento do modelo e gerar os arquivos em sua própria máquina:

### Pré-requisitos
* Python 3.9+ instalado.
* Git instalado.

### Passo a Passo

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/fonsca/world-cup-analytics.git](https://github.com/fonsca/world-cup-analytics.git)
    cd world-cup-analytics
    ```

2.  **Instale as dependências:**
    ```bash
    cd backend
    pip install -r requirements.txt
    ```

3.  **Execute o Pipeline ETL e ML:**
    ```bash
    python gerar_json.py
    ```
    *O script vai baixar os dados da API, treinar o XGBoost e popular a pasta `frontend/dados_json` com as análises preditivas.*

4.  **Acesse o Dashboard:**
    Abra o arquivo `frontend/index.html` no seu navegador para ver o sistema funcionando totalmente *offline* e instantâneo.

---

Desenvolvido por **Mateus Rodrigues Cezar Fonseca** 🎓 Estudante de Sistemas de Informação - UVV  
Foco em: Data Science, Analytics e Engenharia de Dados.

[LinkedIn](https://www.linkedin.com/in/mateusfonseca8/) • [GitHub](https://github.com/fonsca)
