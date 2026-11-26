# ADR-F01: State pattern for the alert status

**Status:** accepted

## Context

A deforestation alert has one of these statuses: PENDENTE, CONFIRMADO, RESOLVIDO and CANCELADO.
Some changes are not permitted. A PENDENTE alert cannot go directly to RESOLVIDO.
Without a pattern, each screen and each controller must repeat the rules in `if/elif` blocks.

## Decision

Use the **State** pattern in `src/model/fiscalizacao/status.py`:

- `StatusAlerta` is the enum of the four statuses.
- Each status has a state class: `Pendente`, `Confirmado`, `Resolvido` and `Cancelado`.
- Each state declares `PROXIMOS`, the states that it can go to:
  - PENDENTE → CONFIRMADO or CANCELADO;
  - CONFIRMADO → RESOLVIDO;
  - RESOLVIDO and CANCELADO are final.
- `RegistroDesmatamento.mudar_status()` sends the change to the current state (`estado.ir_para()`).
  If the transition is not valid, the state raises the exception `TransicaoInvalida`.
  Then the controller returns `(None, "message")`.
- Each state also declares `BLOQUEIA_CONFORMIDADE`.
  A PENDENTE or CONFIRMADO alert stops the compliance declaration.

## Consequences

- The transition rules are in one file only.
- The context menu of the Alertas tab shows only the permitted transitions (`transicoes_possiveis()`).
- The compliance declaration does not repeat the list of statuses that stop it.

## Location in the code

- `src/model/fiscalizacao/status.py`
- `src/model/fiscalizacao/registro_desmatamento.py`: `mudar_status()`
- `src/controller/fiscalizacao/alerta_controller.py`: `mudar_status()`, `transicoes_possiveis()`
