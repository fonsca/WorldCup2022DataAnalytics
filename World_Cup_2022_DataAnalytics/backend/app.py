from flask import Flask, jsonify
from flask_cors import CORS
from analiseWC import obter_dados_partida

app = Flask(__name__)
CORS(app)  # Permite que o Frontend acesse o Backend

@app.route('/api/partida/<match_id>', methods=['GET'])
def get_partida(match_id):
    # Chama a função do arquivo de análise
    dados = obter_dados_partida(match_id)
    return jsonify(dados)

if __name__ == '__main__':
    app.run(debug=True, port=5000)