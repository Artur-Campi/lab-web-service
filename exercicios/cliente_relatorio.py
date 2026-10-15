"""Exercício 1: Cliente integrador (consulta Flask e Node e funde os dados)."""
import requests

URL_FLASK = "http://localhost:5000/detalhes/{}"
URL_NODE = "http://localhost:3000/estoque/{}"


def buscar(url):
    resposta = requests.get(url, timeout=5)
    dados = resposta.json()
    if resposta.status_code != 200:
        raise ValueError(f"HTTP {resposta.status_code}: {dados.get('message', dados)}")
    return dados


def gerar_relatorio(produto_id):
    fiscal = buscar(URL_FLASK.format(produto_id))   # {"id", "preco", "categoria"}
    estoque = buscar(URL_NODE.format(produto_id))   # {"id", "nome", "estoque"}
    return {**fiscal, **estoque}                    # fusão dos dois JSONs


if __name__ == "__main__":
    produto_id = input("Digite o ID do produto: ").strip()
    try:
        p = gerar_relatorio(produto_id)
        print(f"ID: {p['id']} | Nome: {p['nome']} | Preço: R$ {p['preco']} | Estoque: {p['estoque']}")
    except requests.exceptions.ConnectionError:
        print("Erro: não foi possível conectar. Os dois servidores estão rodando?")
    except ValueError as erro:
        print(f"Erro: {erro}")
