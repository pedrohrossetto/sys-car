# ADR-F13: Operations on embargo, declaration and notification

**Status:** accepted

## Context

Class 08 asks for the update and delete operations through the GUI. Issue #5 asks for these operations where they are
applicable. Where they are not applicable, issue #5 asks for a decision in an ADR.

After [ADR-F12](ADR-F12-crud-do-alerta.en.md), the alert has the full CRUD. The evidence is not in the system now
([ADR-F11](ADR-F11-remocao-das-fontes-e-factory-na-declaracao.en.md)). 3 entities were not complete:

| Entity | Before this ADR |
|---|---|
| Embargo | create, show, lift |
| Declaration | create, show |
| Notification | created automatically, show, mark as read |

## Decision

| Entity | Update | Delete |
|---|---|---|
| Embargo | Only the **reason**, with the button "Alterar motivo do selecionado" | **Not available.** "Levantar embargo" (lift the embargo) does this function |
| Declaration | **Not available** | **Not available** |
| Notification | Only the status: "Marcar como lida" (mark as read) | **Not available** |

### Embargo

- The user can correct the reason of an active or a lifted embargo.
- The property, the unit, the alert and the date do **not** change. They record who embargoed which property, and when.
- The system does not delete an embargo. To lift the embargo (`ativo = 0`) removes the block on the property and keeps the history.
  The property record tab and the embargo tab continue to show the lifted embargoes.

### Declaration

- The declaration is a document: it records the result of the analysis on a date. The user can save it in a `.txt` file and
  give it to a person.
- If the system changes or deletes the declaration, the document that the person has is different from the system.
- If the condition of the property changes, the owner asks for a new declaration. The list shows all the declarations,
  from the newest to the oldest.

### Notification

- The system creates the notification (Observer, [ADR-F02](ADR-F02-observer-notificacoes.en.md)). It is the record
  that the unit received the message.
- The only change is the status: from ENVIADA (sent) to LIDA (read).
- The deletion of a notification deletes the proof of the message. Thus, the deletion is not available.

## Exception: cascade deletion

The database still deletes, in cascade (`ON DELETE CASCADE`), the records that the screens cannot delete:

- the deletion of a **property** deletes its embargoes, declarations and notifications;
- the deletion of an **alert** deletes its embargoes and notifications (ADR-F12).

## Rejected alternatives

- **Delete the lifted embargoes:** the list is shorter, but the history of the property is lost.
- **Delete a declaration that the user requested by mistake:** the request has no effect on the other data. A new declaration solves the problem.
- **Delete the read notifications:** the inbox is shorter, but the record of the messages is lost.

## Consequences

- Issue #5 is complete: each entity has the applicable operations. This ADR gives the reasons for the operations that are not available.
- The tables of embargoes, declarations and notifications always become larger. For an academic project, the volume is small.

## Location in the code

- `src/controller/fiscalizacao/conformidade_controller.py`: `alterar_motivo()`, `buscar_embargo()`
- `src/view/fiscalizacao/conformidade_aba.py`: button "Alterar motivo do selecionado"
- `tests/test_fiscalizacao_conformidade.py`: `test_alterar_motivo_do_embargo`
