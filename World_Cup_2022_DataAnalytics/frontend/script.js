let meuGrafico = null; // Variável global para controlar o gráfico

async function carregarDados() {
    try {
        // 1. Conecta na API Python
        const response = await fetch('http://127.0.0.1:5000/api/partida/1');
        const dados = await response.json();

        console.log("Dados recebidos:", dados);

        // 2. Atualiza o Gráfico de Barras
        atualizarGrafico(dados.usage_rate);

        // 3. Atualiza o Mapa de Campo
        plotarNoCampo(dados.mapa_acoes);

    } catch (erro) {
        console.error("Erro ao buscar dados:", erro);
        alert("Certifique-se de que o backend Python está rodando!");
    }
}

function atualizarGrafico(dadosUsage) {
    const ctx = document.getElementById('usageChart').getContext('2d');

    // Prepara os arrays para o Chart.js
    const nomes = dadosUsage.map(d => d.jogador);
    const valores = dadosUsage.map(d => d.usage_rate);

    // Se já existe gráfico, destroi para criar o novo
    if (meuGrafico) meuGrafico.destroy();

    meuGrafico = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: nomes,
            datasets: [{
                label: 'Usage Rate (%)',
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

function plotarNoCampo(acoes) {
    const campo = document.getElementById('campo-futebol');
    
    // Limpa pontos antigos (exceto as linhas do campo)
    const pontosAntigos = document.querySelectorAll('.ponto-acao');
    pontosAntigos.forEach(p => p.remove());

    acoes.forEach(acao => {
        const el = document.createElement('div');
        el.className = 'ponto-acao';
        
        // Posiciona no campo (X e Y vêm da API)
        el.style.left = `${acao.x}%`;
        el.style.top = `${acao.y}%`;
        
        // Tooltip simples
        el.title = `${acao.jogador} - ${acao.tipo}`;
        
        campo.appendChild(el);
    });
}