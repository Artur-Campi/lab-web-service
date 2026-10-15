from flask import Flask, jsonify

app = Flask(__name__)


@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify({
        "mensagem": "Olá do Flask!",
        "status": "sucesso",
        "tecnologia": "Python"
    })


if __name__ == '__main__':
    # host='0.0.0.0' permite acesso externo (ex.: Codespaces)
    app.run(debug=True, host='0.0.0.0', port=5000)
