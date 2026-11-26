# ADR-F02: Observer pattern for the notifications

**Status:** accepted

## Context

The system must tell the competent units when it creates an alert or changes the status of an alert.
The code that records the alert must not know the details of the units that receive the message.

## Decision

Use the **Observer** pattern:

- `ObservadorAlerta` (abstract) declares `atualizar(registro, evento)`.
- `PublicadorAlertas` keeps the list of observers. It gives `inscrever()`, `cancelar_inscricao()` and `notificar()`.
- `NotificadorUnidades` is the concrete observer. It creates one `Notificacao` for **each** registered competent unit.
- The `AlertaController` calls `publicador.notificar()` after it creates an alert and after each status change.
- The `AlertaController` accepts a different publisher in the constructor. The tests use this to replace the observers.
- Without a publisher in the constructor, the `AlertaController` uses the single publisher of the system (see [ADR-F08](ADR-F08-singleton-publicador-alertas.en.md)).

## Consequences

- A new type of message (for example, e-mail) is a new observer. The controller does not change.
- If there are no registered units, the system does not create notifications. This does not cause an error.
- A notification is only a row in the database. The system does not send real messages.

## Location in the code

- `src/model/fiscalizacao/observador.py`
- `src/model/fiscalizacao/notificador.py`
- `src/controller/fiscalizacao/alerta_controller.py`
