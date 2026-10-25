# dispara 10 pedidos de agendamento ao mesmo tempo para o mesmo horario
import sys
import threading
from collections import Counter

import requests

URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
HORARIO = sys.argv[2] if len(sys.argv) > 2 else "2025-12-01T03:00:00Z"
N = 10

barreira = threading.Barrier(N)  # todas as threads saem juntas
resultados = [None] * N


def pedido(i):
    corpo = {"cientista_id": (i % 3) + 1, "telescopio_id": 1,
             "horario_inicio_utc": HORARIO, "horario_fim_utc": HORARIO.replace("03:00", "03:05")}
    barreira.wait()
    r = requests.post(f"{URL}/agendamentos", json=corpo, timeout=30)
    resultados[i] = r.status_code
    print(f"pedido {i + 1:2d} (cientista {corpo['cientista_id']}) -> HTTP {r.status_code}")


threads = [threading.Thread(target=pedido, args=(i,)) for i in range(N)]
for t in threads:
    t.start()
for t in threads:
    t.join()

print("\nresumo:", dict(Counter(resultados)))
ativos = [a for a in requests.get(f"{URL}/agendamentos").json()
          if a["horario_inicio_utc"] == HORARIO and a["status"] == "ATIVO"]
print(f"agendamentos ATIVOS no banco para {HORARIO}: {len(ativos)}")
