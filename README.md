# ⚽ World Cup 2022 Analytics: End-to-End Machine Learning

> **Uma aplicação Full-Stack de Ciência de Dados que processa partidas da Copa do Mundo em tempo real, aplica modelos de Machine Learning (XGBoost) para calcular métricas avançadas (VAEP) e visualiza táticas em um dashboard interativo.**

## 📊 Sobre o Projeto

Este projeto não é apenas uma análise estática. É uma **ETL Pipeline** completa que consome dados brutos da API da StatsBomb, processa eventos táticos e treina um modelo de Machine Learning em tempo de execução para avaliar a performance dos jogadores.

O objetivo foi simular o dia-a-dia de um Engenheiro de Dados e Cientista de Dados, resolvendo problemas como:
* Extração de dados via API.
* Limpeza e transformação de coordenadas espaciais.
* Utilização de métricas avançadas (VAEP - Valuing Actions by Estimating Probabilities).
* Desenvolvimento de API (Backend) e Dashboard Interativo (Frontend).

---

## 📸 Screenshots

| Mapa Geral (Todos) | Filtro por Jogador | Análise de Eficiência (ML) |
|:---:|:---:|:---:|
| <img src="data/TodosJogadores.png" width="300"> | <img src="data/MapaFiltrado.png" width="300"> | <img src="data/URxVAEP.png" width="300"> |
| *Visão tática global* | *Ações individuais* | *Clusterização Usage x VAEP* |

---

## 🛠 Tecnologias e Ferramentas

### Backend (Python)
* **Flask:** Criação da API RESTful para servir os dados ao frontend.
* **StatsBombPy:** Extração de dados oficiais da Copa 2022.
* **Pandas & NumPy:** Manipulação e limpeza de dados (Data Wrangling).
* **XGBoost:** Algoritmo de Gradient Boosting treinado para calcular a probabilidade de gol de cada ação (VAEP simplificado).
* **Scikit-Learn:** Pré-processamento de features (Label Encoding).

### Frontend (Web)
* **JavaScript (Vanilla):** Lógica de consumo de API (Fetch) e manipulação do DOM.
* **Chart.js:** Renderização de gráficos de dispersão (Scatter) e barras.
* **HTML5 & CSS3:** Layout responsivo e design do campo de futebol vertical.

---

## A Lógica de Machine Learning (VAEP)

Para ir além das estatísticas básicas (gols e assistências), implementei um modelo de **Valoração de Ações**.

1.  **O Problema:** Um passe no meio de campo vale menos que um passe na pequena área, mas estatísticas comuns tratam ambos como "1 passe".
2.  **A Solução (XGBoost):**
    * O sistema coleta as coordenadas (X, Y) e o tipo de cada ação.
    * Treina um classificador `XGBClassifier` para prever: *"Essa jogada resultou em gol nos próximos 10 segundos?"*.
    * A probabilidade gerada (0 a 1) se torna o "Valor VAEP" da ação.
3.  **Resultado:** Conseguimos identificar jogadores que não fazem gols, mas criam as jogadas mais perigosas (Quadrante Superior Direito do Gráfico de Dispersão).

---

## 🚀 Como Rodar o Projeto

### Pré-requisitos
* Python instalado.
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

3.  **Execute o servidor:**
    ```bash
    python app.py
    ```
    *O terminal deve exibir: `Running on http://127.0.0.1:5000`*

4.  **Acesse o Dashboard:**
    Abra o arquivo `frontend/index.html` no seu navegador preferido.

---

Desenvolvido por **Mateus Rodrigues Cezar Fonseca** 🎓 Estudante de Sistemas de Informação - UVV  
Foco em: Data Science, Analytics e Engenharia de Dados.

[LinkedIn](https://www.linkedin.com/in/mateusfonseca8/) • [GitHub](https://github.com/fonsca)