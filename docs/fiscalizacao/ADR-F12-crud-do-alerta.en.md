# ADR-F12: CRUD of the deforestation alert

**Status:** accepted. Changed by [ADR-F14](ADR-F14-ponto-do-alerta-define-a-propriedade.en.md): the update does not change the coordinates now.

## Context

Class 08 asks for the 4 operations through the GUI: create, read, update and delete.
The user could only create and show an alert. The only possible change was the status change through the State pattern (ADR-F01).

## Decision

The `AlertaController` has the full CRUD, as the other controllers have. The model continues to inherit the data access from
`ModeloBase` (Template Method, ADR-F09).

| Operation | Method | Rule |
|---|---|---|
| Create | `criar(propriedade_id, descricao, latitude, longitude, data=None)` | Each alert starts as PENDENTE. The units receive a notification (Observer). |
| Read | `buscar_por_id(id)`, `listar(incluir_finalizados=True)` | |
| Update | `atualizar(id, descricao, latitude, longitude, data=None)` | Changes only the description, the date and the coordinates, in all statuses. It does not make a notification. |
| Delete | `excluir(id)` | Deletes the alert. The database also deletes the notifications and the **embargoes** of the alert (cascade). |

- `atualizar()` does not change the **status**. Only `mudar_status()` changes it, with the transitions of the State pattern.
- The **property** of the alert does not change. The embargoes point to the alert and to the property. The two must agree.
- In the Alertas tab, a double-click (or Enter) puts the alert in the form. Salvar (save) creates or updates. Excluir (delete) asks
  for a confirmation. It tells the user that the system also deletes the embargoes and the notifications of the alert.

## Rejected alternatives

- **Stop the deletion of an alert with an embargo:** this is safer, but the team selected the free deletion.
- **Permit the deletion only of PENDENTE or CANCELADO alerts:** the same reason.
- **Explicit CRUD methods in the model:** they repeat `ModeloBase` and make the Template Method weaker.

## Accepted risk

The deletion of a CONFIRMADO alert also deletes its embargo. Then the property can stop being embargoed, and no
unit lifted the embargo. The confirmation on the screen tells the user about this.

## Location in the code

- `src/controller/fiscalizacao/alerta_controller.py`: `criar()`, `atualizar()`, `excluir()`
- `src/view/fiscalizacao/alertas_aba.py`: form with Salvar, Excluir and Limpar
- `tests/test_fiscalizacao_alertas.py`
