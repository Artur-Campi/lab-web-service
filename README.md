# Laboratório Web Service - Computação Distribuída

Aluno: Artur Campi (RA 10436740) - Universidade Presbiteriana Mackenzie

Comunicação entre serviços REST em **Python/Flask** (porta 5000) e **Node.js/Express** (porta 3000).

## Estrutura

```
exemplo-aula/          Exemplo da aula (seções 4 a 6)
  aula-flask/app.py      GET /api/data
  aula-node/index.js     GET /api/data
  cliente.py             consome os dois servidores
exercicios/
  flask/app.py           produtos_fiscais, /detalhes/<id>, /status, POST /fiscal/cadastrar
  node/server.js         produtos_estoque, /estoque/:id, /api/full-info/:id, /status, POST /cadastrar
  cliente_relatorio.py   Exercício 1 - cliente integrador
  cliente_status.py      Exercício 3 - monitoramento genérico
  cliente_cadastro.py    Exercício 4 - cadastro distribuído
  cliente_erros.py       Exercício 5 - validação de ID (400 INVALID_ID)
```

## Como rodar (Codespaces)

```bash
pip install -r requirements.txt
(cd exemplo-aula/aula-node && npm install)
(cd exercicios/node && npm install)

# terminal 1
cd exercicios/flask && python3 app.py
# terminal 2
cd exercicios/node && node server.js
# terminal 3
cd exercicios && python3 cliente_relatorio.py
```
