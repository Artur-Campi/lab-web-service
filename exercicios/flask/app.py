# servidor flask - porta 5000 (parte fiscal)
from datetime import datetime, timezone

from flask import Flask, jsonify, request

app = Flask(__name__)
app.json.ensure_ascii = False  # pra nao virar \u00e1 no json

# base fiscal
produtos_fiscais = {
    "1": {"preco": 2500.0, "categoria": "Laptops"},
    "2": {"preco": 1200.0, "categoria": "Monitores"},
}

# ex 4 - produtos que vem do node
produtos_tecnicos = {}

TAXA_IMPOSTO = 0.20


def agora_iso():
    # mesmo formato do toISOString() do js
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def id_valido(valor):
    # ex 5 - so aceita numero inteiro positivo
    texto = str(valor)
    return texto.isdigit() and int(texto) > 0


def erro_id_invalido():
    return jsonify({
        "error": "INVALID_ID",
        "message": "O ID deve ser um inteiro positivo",
    }), 400


def buscar_produto(produto_id):
    return produtos_fiscais.get(produto_id) or produtos_tecnicos.get(produto_id)


@app.route("/api/data", methods=["GET"])
def get_data():
    return jsonify({"mensagem": "Olá do Flask!", "status": "sucesso", "tecnologia": "Python"})


@app.route("/detalhes/<produto_id>", methods=["GET"])
def detalhes(produto_id):
    if not id_valido(produto_id):
        return erro_id_invalido()

    produto_id = str(int(produto_id))  # "01" vira "1"
    produto = buscar_produto(produto_id)
    if produto is None:
        return jsonify({"error": "NOT_FOUND", "message": f"Produto {produto_id} não encontrado"}), 404

    return jsonify({"id": produto_id, **produto})


@app.route("/status", methods=["GET"])
def status():
    return jsonify({"service": "flask-fiscal", "status": "online", "timestamp": agora_iso()})


@app.route("/fiscal/cadastrar", methods=["POST"])
def fiscal_cadastrar():
    dados = request.get_json(silent=True) or {}

    if not id_valido(dados.get("id", "")):
        return erro_id_invalido()

    try:
        preco_base = float(dados["preco_base"])
        categoria = str(dados["categoria"])
    except (KeyError, TypeError, ValueError):
        return jsonify({
            "error": "INVALID_DATA",
            "message": "Campos obrigatórios: preco_base (número) e categoria (texto)",
        }), 400

    produto_id = str(int(dados["id"]))
    preco_calculado = round(preco_base * (1 + TAXA_IMPOSTO), 2)

    produtos_tecnicos[produto_id] = {"preco": preco_calculado, "categoria": categoria}
    print(f"[FISCAL] Produto {produto_id} cadastrado: {produtos_tecnicos[produto_id]}")

    return jsonify({"id": produto_id, **produtos_tecnicos[produto_id]}), 201


@app.route("/fiscal/produtos", methods=["GET"])
def listar_produtos_tecnicos():
    # so pra conferir o dicionario no ex 4
    return jsonify(produtos_tecnicos)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
