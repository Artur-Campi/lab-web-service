# MODELOS.md - Entidades do SCTEC

Banco: SQLite (`agendamentos.db`), acessado pelo serviço de agendamento via SQLAlchemy.
Todos os horários são guardados em UTC no formato ISO-8601 (`2025-12-01T03:00:00Z`).

## Cientista

Quem pede tempo de observação no telescópio.

| campo        | tipo        | regra                     |
|--------------|-------------|---------------------------|
| id           | inteiro     | chave primária            |
| nome         | texto(120)  | obrigatório               |
| email        | texto(120)  | obrigatório e único       |
| instituicao  | texto(120)  | opcional                  |

## Telescopio

O equipamento que está sendo disputado.

| campo        | tipo        | regra                     |
|--------------|-------------|---------------------------|
| id           | inteiro     | chave primária            |
| nome         | texto(60)   | obrigatório e único (ex.: `Hubble-Acad`) |
| localizacao  | texto(120)  | opcional                  |

## Agendamento

Uma reserva de um slot do telescópio para um cientista.

| campo              | tipo        | regra                                         |
|--------------------|-------------|-----------------------------------------------|
| id                 | inteiro     | chave primária                                |
| cientista_id       | inteiro     | FK para Cientista, obrigatório                |
| telescopio_id      | inteiro     | FK para Telescopio, obrigatório               |
| horario_inicio_utc | texto ISO   | obrigatório                                   |
| horario_fim_utc    | texto ISO   | obrigatório (se não vier, usa o início)       |
| status             | texto       | `ATIVO` ou `CANCELADO`                        |
| criado_em_utc      | texto ISO   | preenchido pelo servidor (hora do servidor)   |

## Relacionamentos

- Um Cientista tem vários Agendamentos (1:N).
- Um Telescopio tem vários Agendamentos (1:N).

## Regra de negócio principal

Não pode existir mais de um agendamento **ATIVO** para o mesmo telescópio no mesmo `horario_inicio_utc`.

O recurso que vai para o coordenador (lock) é identificado como:

```
<nome do telescopio>_<horario_inicio_utc>
ex.: Hubble-Acad_2025-12-01T03:00:00Z
```

## Recurso do coordenador (não fica no banco)

O serviço Node guarda os locks só em memória:

| campo    | tipo   | descrição                                   |
|----------|--------|---------------------------------------------|
| recurso  | texto  | chave do lock (formato acima)               |
| desde    | ISO    | quando o lock foi concedido                 |
