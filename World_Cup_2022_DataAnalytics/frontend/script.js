let dadosGlobais = []; // Guarda os dados para não recarregar
let meuGrafico = null;
let scatterChart = null; // Variável global

// Ao carregar a página, busca a lista de jogos primeiro
window.onload = async function() {
    await carregarListaJogos();
    // Depois carrega os dados do primeiro jogo da lista (ou da final)
    carregarDados();
};

async function carregarListaJogos() {
    try {
        const response = await fetch('./dados_json/lista_jogos.json');
        const jogos = await response.json();
        
        const select = document.getElementById('selecao-partida');
        select.innerHTML = ''; // Limpa

        jogos.forEach(jogo => {
            const option = document.createElement('option');
            option.value = jogo.match_id;
            option.innerText = `${jogo.fase}: ${jogo.descricao}`;
            
            // Se for a final (ID 3869685), deixa selecionada por padrão
            if (jogo.match_id === 3869685) option.selected = true;
            
            select.appendChild(option);
        });

    } catch (erro) {
        console.error("Erro ao listar jogos:", erro);
        alert("Erro ao baixar lista de jogos.");
    }
}

async function carregarDados() {
    const btn = document.querySelector('button');
    const selectPartida = document.getElementById('selecao-partida');
    
    // Pega o ID do jogo selecionado no dropdown
    const matchId = selectPartida.value;

    btn.innerText = "Carregando...";
    btn.disabled = true;

    try {
        const response = await fetch(`./dados_json/partida_${matchId}.json`);
        const dados = await response.json();

        if (dados.erro) {
            alert("Erro no Backend: " + dados.erro);
            return;
        }

        // Salva na variavel global
        dadosGlobais = dados.mapa_acoes;
        
        // 1. Desenha tudo inicialmente
        plotarNoCampo(dadosGlobais);
        atualizarGrafico(dados.usage_rate);
        atualizarScatter(dados.scatter_data);

        if (typeof atualizarTabela === "function") {
            atualizarTabela(dados.todos_jogadores);
        }
        
        // 2. Preenche o Select com os nomes dos jogadores
        preencherSelect(dados.todos_jogadores);

        // 3. Atualiza a tabela
        atualizarTabela(dados.tabela_stats);

    } catch (erro) {
        console.error("Erro JS:", erro);
        alert("Erro ao buscar dados. Veja o console.");
    } finally {
        btn.innerText = "Carregar Dados da Partida";
        btn.disabled = false;
    }
}

function preencherSelect(listaNomes) {
    const select = document.getElementById('filtro-jogador');
    
    // Mantém a opção "Todos"
    select.innerHTML = '<option value="todos">Todos os Jogadores</option>';

    listaNomes.forEach(nome => {
        const option = document.createElement('option');
        
        // Verifica se o item é um Texto ou um Objeto (para evitar [object Object])
        if (typeof nome === 'object') {
            // Se por acaso vier um objeto, tentamos pegar a propriedade .jogador
            option.value = nome.jogador || "Erro";
            option.innerText = nome.jogador || "Erro";
        } else {
            // Se for texto normal (o esperado)
            option.value = nome;
            option.innerText = nome;
        }
        
        select.appendChild(option);
    });
}
function filtrarPorJogador() {
    const jogadorSelecionado = document.getElementById('filtro-jogador').value;

    if (jogadorSelecionado === "todos") {
        plotarNoCampo(dadosGlobais);
    } else {
        // Filtra o array no JavaScript (Array.filter)
        const dadosFiltrados = dadosGlobais.filter(acao => acao.jogador === jogadorSelecionado);
        plotarNoCampo(dadosFiltrados);
    }
}

function plotarNoCampo(acoes) {
    const campo = document.getElementById('campo-futebol');
    // Remove bolinhas antigas
    document.querySelectorAll('.ponto-acao').forEach(p => p.remove());

    acoes.forEach(acao => {
        const el = document.createElement('div');
        el.className = 'ponto-acao';
        
// --- CORES ---
        if (acao.is_goal) {
            // Se for GOL: Amarelo Ouro, maior e por cima de todos
            el.style.backgroundColor = "#FFD700"; // Gold
            el.style.width = "18px";
            el.style.height = "18px";
            el.style.zIndex = "100";
            el.style.border = "2px solid black"; // Borda para destacar
        } 
        else if (acao.tipo === "Shot") {
            // Se for Chute (mas não gol): Vermelho
            el.style.backgroundColor = "red";
            el.style.zIndex = "10";
        }

        // --- POSICIONAMENTO VERTICAL ---
        // Agora usamos 'bottom' (distância do fundo) e 'left'
        el.style.left = `${acao.left}%`;
        el.style.bottom = `${acao.bottom}%`; // Mudou de top para bottom
        
        // Tooltip
        let texto = `${acao.jogador} (${acao.tipo})`;
        if(acao.is_goal) texto += " ⚽ GOL!";
        el.title = texto;
        
        campo.appendChild(el);
    });
}

// ... Mantenha a função atualizarGrafico() igual à anterior ...
function atualizarGrafico(dadosUsage) {
    const ctx = document.getElementById('usageChart').getContext('2d');
    const nomes = dadosUsage.map(d => d.jogador);
    const valores = dadosUsage.map(d => d.usage_rate);

    if (meuGrafico) meuGrafico.destroy();

    meuGrafico = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: nomes,
            datasets: [{
                label: 'Volume de Jogo (%)',
                data: valores,
                backgroundColor: '#00ff88',
                color: '#fff'
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { labels: { color: 'white' } } },
            scales: {
                y: { ticks: { color: 'white' } },
                x: { ticks: { color: 'white' } }
            }
        }
    });
}

function atualizarTabela(stats) {
    const tbody = document.getElementById('tabela-corpo');
    tbody.innerHTML = ''; // Limpa a tabela antes de encher

    stats.forEach(jogador => {
        const tr = document.createElement('tr');
        
        tr.innerHTML = `
            <td>${jogador.nome}</td>
            <td>${jogador.passes}</td>
            <td>${jogador.chutes}</td>
        `;
        
        tbody.appendChild(tr);
    });
}

function atualizarScatter(dadosScatter) {
    const ctx = document.getElementById('scatterChart').getContext('2d');

    if (scatterChart) scatterChart.destroy();

    scatterChart = new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'Jogadores',
                data: dadosScatter, // O formato já é {x: 10, y: 0.5, jogador: "Messi"}
                backgroundColor: 'rgba(0, 255, 136, 0.6)', // Verde Neon
                borderColor: 'rgba(255, 255, 255, 0.8)',
                borderWidth: 1,
                pointRadius: 6,
                pointHoverRadius: 10
            }]
        },
        options: {
            responsive: true,
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            // Mostra o nome do jogador no mouseover
                            let ponto = context.raw;
                            return `${ponto.jogador}: Usage ${ponto.x}% | VAEP ${ponto.y}`;
                        }
                    }
                },
                legend: { display: false }
            },
            scales: {
                x: {
                    title: { display: true, text: 'Usage Rate (%)', color: 'white' },
                    ticks: { color: 'white' },
                    grid: { color: '#444' }
                },
                y: {
                    title: { display: true, text: 'VAEP (Perigo Criado)', color: 'white' },
                    ticks: { color: 'white' },
                    grid: { color: '#444' }
                }
            }
        }
    });
}