# sctec-projeto

Sistema de Controle de Telescópio Espacial Compartilhado (atividade de Computação Distribuída, Mackenzie).
Artur Campi - RA 10436740

- `servico-agendamento/`: Flask + SQLAlchemy (porta 5000)
- `servico-coordenador/`: Node + Express, locks (porta 3000)
- `MODELOS.md`, `API.md`, `LOGGING.md`: entrega 1
- `teste_estresse.py`: 10 requisições ao mesmo tempo

## Rodando sem docker

```bash
cd servico-agendamento
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python app.py                 # USAR_LOCK=false python app.py para ver a condição de corrida

cd servico-coordenador
npm install && node server.js

python teste_estresse.py
```

## Rodando com docker

```bash
docker-compose up --build
docker-compose logs -f
```

Cliente web: abrir a porta 5000 no navegador.
