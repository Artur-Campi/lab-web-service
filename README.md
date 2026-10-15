# lab-web-service

Lab de Web Services de Computação Distribuída (Mackenzie).
Artur Campi - RA 10436740

Flask na porta 5000 e Node/Express na porta 3000.

- `exemplo-aula/`: exemplos da aula (app.py, index.js e cliente.py)
- `exercicios/`: servidores e clientes dos exercícios 1 a 5

## Como rodar

```bash
pip install -r requirements.txt
cd exercicios/node && npm install && cd ../..

# terminal 1
cd exercicios/flask && python3 app.py
# terminal 2
cd exercicios/node && node server.js
# terminal 3
cd exercicios && python3 cliente_relatorio.py
```
