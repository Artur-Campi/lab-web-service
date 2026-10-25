# API.md - Endpoints do SCTEC

Todas as respostas são JSON. Os recursos trazem um campo `_links` (HATEOAS) com as próximas ações possíveis,
cada link com `href` e `method`.

Erros seguem sempre o mesmo formato:

```json
{ "error": "CODIGO", "message": "texto explicando" }
```

---

## Serviço de Agendamento (Flask, porta 5000)

### GET /time
Hora oficial do servidor (fonte da verdade para o cliente sincronizar o relógio).

```json
{ "timestamp_utc": "2026-10-25T18:58:08.709Z", "epoch_ms": 1792954688709 }
```

### GET /cientistas e GET /cientistas/{id}
```json
{
  "id": 1, "nome": "Marie Curie", "email": "marie@sctec.edu", "instituicao": "Sorbonne",
  "_links": {
    "self":         { "href": "/cientistas/1", "method": "GET" },
    "agendamentos": { "href": "/agendamentos?cientista_id=1", "method": "GET" }
  }
}
```

### GET /telescopios e GET /telescopios/{id}
```json
{ "id": 1, "nome": "Hubble-Acad", "localizacao": "Orbita baixa",
  "_links": { "self": { "href": "/telescopios/1", "method": "GET" } } }
```

### GET /agendamentos
Lista todos (aceita `?cientista_id=`). Cada item tem o mesmo formato do GET por id.

### GET /agendamentos/{id}
```json
{
  "id": 1, "cientista_id": 2, "cientista": "Carl Sagan",
  "telescopio_id": 1, "telescopio": "Hubble-Acad",
  "horario_inicio_utc": "2025-12-01T03:00:00Z", "horario_fim_utc": "2025-12-01T03:05:00Z",
  "status": "ATIVO", "criado_em_utc": "2026-10-25T18:58:00.413Z",
  "_links": {
    "self":       { "href": "/agendamentos/1", "method": "GET" },
    "cientista":  { "href": "/cientistas/2",   "method": "GET" },
    "telescopio": { "href": "/telescopios/1",  "method": "GET" },
    "cancelar":   { "href": "/agendamentos/1", "method": "DELETE" }
  }
}
```

O link `cancelar` **só aparece quando o status é ATIVO**. Depois de cancelado ele some, e é isso que o
cliente web usa para habilitar ou não o botão.

### POST /agendamentos
Corpo:
```json
{
  "cientista_id": 1,
  "telescopio_id": 1,
  "horario_inicio_utc": "2025-12-01T03:00:00Z",
  "horario_fim_utc": "2025-12-01T03:05:00Z",
  "timestamp_cliente_utc": "2026-10-25T18:57:59.900Z"
}
```

Fluxo:
1. pede lock ao coordenador para `Hubble-Acad_2025-12-01T03:00:00Z`
2. se negar, responde 409
3. com o lock: verifica conflito no BD, salva, grava log de auditoria
4. libera o lock (no `finally`, mesmo se der erro)

| status | quando                                             |
|--------|----------------------------------------------------|
| 201    | criado (corpo igual ao GET /agendamentos/{id})     |
| 400    | faltou campo (`INVALID_DATA`)                      |
| 404    | cientista ou telescópio não existe                 |
| 409    | recurso travado por outro pedido ou horário já ocupado (`CONFLICT`) |
| 503    | coordenador fora do ar                             |

### DELETE /agendamentos/{id}
Cancela (muda o status para CANCELADO, não apaga do banco). Gera log de auditoria `AGENDAMENTO_CANCELADO`.

| status | quando                         |
|--------|--------------------------------|
| 200    | cancelado (volta o agendamento sem o link `cancelar`) |
| 404    | não existe                     |
| 409    | já estava cancelado (`ALREADY_CANCELLED`) |

### GET /
Entrega o `index.html` (cliente web da Entrega 4).

---

## Serviço Coordenador (Node/Express, porta 3000)

### POST /lock
```json
{ "recurso": "Hubble-Acad_2025-12-01T03:00:00Z" }
```
- `200 { "status": "concedido", "recurso": "..." }` se estava livre
- `409 { "status": "negado", "recurso": "..." }` se já está travado

### POST /unlock
```json
{ "recurso": "Hubble-Acad_2025-12-01T03:00:00Z" }
```
- `200 { "status": "liberado" }`
- `404 { "status": "nao_estava_travado" }`

### GET /locks
Mostra os locks ativos no momento (só para depurar).
