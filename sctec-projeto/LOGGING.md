# LOGGING.md - Formato dos logs

Todos os horários dos logs são UTC com milissegundos (`2025-10-26T18:00:05.123Z`).

## 1. Log de aplicação (serviço de agendamento)

Vai para o `app.log` e para o console ao mesmo tempo (módulo `logging` do Python).

Formato:
```
NIVEL:TIMESTAMP_UTC:servico-agendamento:mensagem
```

Exemplos:
```
INFO:2025-10-26T18:00:04.500Z:servico-agendamento:Requisição recebida para POST /agendamentos (recurso Hubble-Acad_2025-12-01T03:00:00Z)
INFO:2025-10-26T18:00:04.505Z:servico-agendamento:Tentando adquirir lock para o recurso Hubble-Acad_2025-12-01T03:00:00Z
INFO:2025-10-26T18:00:05.120Z:servico-agendamento:Lock adquirido com sucesso para o recurso Hubble-Acad_2025-12-01T03:00:00Z
INFO:2025-10-26T18:00:05.122Z:servico-agendamento:Iniciando verificação de conflito no BD
INFO:2025-10-26T18:00:05.123Z:servico-agendamento:Salvando novo agendamento no BD
INFO:2025-10-26T18:00:05.130Z:servico-agendamento:Liberando lock para o recurso Hubble-Acad_2025-12-01T03:00:00Z
INFO:2025-10-26T18:00:05.121Z:servico-agendamento:Falha ao adquirir lock para o recurso Hubble-Acad_2025-12-01T03:00:00Z, recurso ocupado
INFO:2025-10-26T18:00:06.000Z:servico-agendamento:Requisição recebida em GET /time do IP 127.0.0.1
```

Mensagens usadas:

| momento                         | mensagem                                                  |
|---------------------------------|-----------------------------------------------------------|
| chegou POST                     | Requisição recebida para POST /agendamentos (recurso X)    |
| antes de chamar o coordenador   | Tentando adquirir lock para o recurso X                    |
| coordenador respondeu 200       | Lock adquirido com sucesso para o recurso X                |
| coordenador respondeu 409       | Falha ao adquirir lock para o recurso X, recurso ocupado   |
| antes da consulta               | Iniciando verificação de conflito no BD                    |
| antes do commit                 | Salvando novo agendamento no BD                            |
| no finally                      | Liberando lock para o recurso X                            |
| chegou GET /time                | Requisição recebida em GET /time do IP x.x.x.x             |
| chegou DELETE                   | Requisição recebida para DELETE /agendamentos/{id}         |

## 2. Log de auditoria (negócio)

Usa um nível novo chamado **AUDIT** (valor 25, fica entre INFO e WARNING). A mensagem é um JSON e é gravada
no mesmo `app.log`, só depois que o banco confirmou a operação.

```
AUDIT:2025-10-26T18:00:05.125Z:servico-agendamento:{json abaixo}
```

```json
{
  "timestamp_utc": "2025-10-26T18:00:05.123Z",
  "level": "AUDIT",
  "event_type": "AGENDAMENTO_CRIADO",
  "service": "servico-agendamento",
  "details": {
    "agendamento_id": 123,
    "cientista_id": 7,
    "telescopio": "Hubble-Acad",
    "horario_inicio_utc": "2025-12-01T03:00:00Z",
    "timestamp_cliente_utc": "2025-10-26T18:00:04.498Z"
  }
}
```

Eventos:

| event_type             | quando                                  |
|------------------------|-----------------------------------------|
| AGENDAMENTO_CRIADO     | POST /agendamentos salvou com sucesso   |
| AGENDAMENTO_CANCELADO  | DELETE /agendamentos/{id} cancelou      |

## 3. Log do coordenador (Node)

`console.log`, então aparece no terminal e no `docker-compose logs`.

```
[TIMESTAMP_UTC] servico-coordenador: mensagem
```

```
[2025-10-26T18:00:04.510Z] servico-coordenador: Recebido pedido de lock para recurso Hubble-Acad_2025-12-01T03:00:00Z
[2025-10-26T18:00:04.510Z] servico-coordenador: Lock concedido para recurso Hubble-Acad_2025-12-01T03:00:00Z
[2025-10-26T18:00:04.520Z] servico-coordenador: Recurso Hubble-Acad_2025-12-01T03:00:00Z já em uso, negando lock.
[2025-10-26T18:00:05.131Z] servico-coordenador: Recebido pedido de unlock para recurso Hubble-Acad_2025-12-01T03:00:00Z
[2025-10-26T18:00:05.131Z] servico-coordenador: Lock para o recurso Hubble-Acad_2025-12-01T03:00:00Z liberado.
```
