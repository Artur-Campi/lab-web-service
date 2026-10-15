import requests

url_flask = "http://localhost:5000/api/data"
url_node = "http://localhost:3000/api/data"


def consumir_api(nome, url):
    try:
        response = requests.get(url)
        dados = response.json()
        print(f"--- Resposta do {nome} ---")
        print(f"Mensagem: {dados['mensagem']}")
        print(f"Tecnologia: {dados['tecnologia']}\n")
    except Exception:
        print(f"Erro ao conectar no {nome}: Servidor está rodando?")


if __name__ == "__main__":
    consumir_api("Flask", url_flask)
    consumir_api("Node", url_node)
