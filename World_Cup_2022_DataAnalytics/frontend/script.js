let dadosGlobais = []; // Guarda os dados para não recarregar
let meuGrafico = null;

async function carregarDados() {
    const btn = document.querySelector('button');
    btn.innerText = "Carregando...";
    btn.disabled = true;

    try {
        const response = await fetch('http://127.0.0.1:5000/api/partida/0');
        const dados = await response.json();

        // Salva na variavel global
        dadosGlobais = dados.mapa_acoes;
        
        // 1. Desenha tudo inicialmente
        plotarNoCampo(dadosGlobais);
        atualizarGrafico(dados.usage_rate);
        
        // 2. Preenche o Select com os nomes dos jogadores
        preencherSelect(dados.usage_rate); // Usamos a lista de usage que já tem os nomes únicos

    } catch (erro) {
        console.error("Erro:", erro);
        alert("Erro ao buscar dados. Veja o console.");
    } finally {
        btn.innerText = "Carregar Dados da Partida";
        btn.disabled = false;
    }
}

function preencherSelect(listaJogadores) {
    const select = document.getElementById('filtro-jogador');
    // Limpa opções antigas (deixa só o "Todos")
    select.innerHTML = '<option value="todos">Todos os Jogadores</option>';

    listaJogadores.forEach(item => {
        const option = document.createElement('option');
        option.value = item.jogador;
        option.innerText = item.jogador;
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
        
        // Se for chute (Shot), pinta de outra cor (Vermelho)
        if(acao.tipo === "Shot") {
            el.style.backgroundColor = "red";
            el.style.zIndex = "10"; // Fica por cima
        }

        el.style.left = `${acao.x}%`;
        el.style.top = `${acao.y}%`;
        el.title = `${acao.jogador} (${acao.tipo})`;
        
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