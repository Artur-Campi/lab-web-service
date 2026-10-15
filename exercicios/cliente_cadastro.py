# exercicio 4 - cadastro pelo node
import json

import requests

produto = {"id": "3", "nome": "teclado", "estoque": 20, "preco_base": 200.0, "categoria": "Perifericos"}

print(">>> POST http://localhost:3000/cadastrar")
print(json.dumps(produto, ensure_ascii=False))
resposta = requests.post("http://localhost:3000/cadastrar", json=produto, timeout=5)
print(f"\n<<< HTTP {resposta.status_code}")
print(json.dumps(resposta.json(), indent=2, ensure_ascii=False))

print("\n>>> Conferindo produtos_comerciais (Node):")
print(json.dumps(requests.get("http://localhost:3000/comerciais").json(), ensure_ascii=False))

print(">>> Conferindo produtos_tecnicos (Flask):")
print(json.dumps(requests.get("http://localhost:5000/fiscal/produtos").json(), ensure_ascii=False))

print("\n>>> GET http://localhost:3000/api/full-info/3 (produto novo via proxy):")
print(json.dumps(requests.get("http://localhost:3000/api/full-info/3").json(), ensure_ascii=False))
