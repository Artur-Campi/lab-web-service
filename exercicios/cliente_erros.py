# exercicio 5 - testando ids invalidos
import json

import requests

urls = [
    "http://localhost:3000/estoque/-5",
    "http://localhost:3000/estoque/abc",
    "http://localhost:3000/api/full-info/-1",
    "http://localhost:5000/detalhes/-5",
    "http://localhost:5000/detalhes/xyz",
    "http://localhost:3000/estoque/1",   # esse aqui é valido
]

for url in urls:
    r = requests.get(url, timeout=5)
    print(f"GET {url:<42} -> HTTP {r.status_code} {json.dumps(r.json(), ensure_ascii=False)}")
