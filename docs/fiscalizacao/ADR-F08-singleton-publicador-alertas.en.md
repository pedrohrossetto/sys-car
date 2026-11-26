# ADR-F08: Singleton pattern for the alert publisher

**Status:** accepted

## Context

The `PublicadorAlertas` keeps the list of the observers that receive the alert messages (see [ADR-F02](ADR-F02-observer-notificacoes.en.md)).
Before this decision, each `AlertaController` created a new publisher.
The application has only one `AlertaController`, in the Alertas tab. But the code did not make sure of this.
If a different screen created an `AlertaController`, that screen had a different list of observers.
Then an observer registered on one screen did not receive the messages from the other screen.

The `AlertaController` also accepts a publisher in the constructor.
The tests use this to replace the observers. The Singleton must not stop these tests.

## Decision

Use the **Singleton** pattern in `PublicadorAlertas`. The access is through the class:

- `PublicadorAlertas.instancia()` always returns the same object. The first call creates it.
- Without a publisher in the constructor, the `AlertaController` uses `PublicadorAlertas.instancia()`.
- With a publisher in the constructor, the `AlertaController` uses that publisher. The tests do not change.
- The controller module creates the `NotificadorUnidades` one time.
  `inscrever()` ignores an observer that is already registered. Thus, more controllers do not make duplicate notifications.

### Why the constructor is not locked

The usual Python Singleton replaces `__new__`. Then `PublicadorAlertas()` always returns the same object.
The team rejected this solution for two reasons:

1. The tests create `PublicadorAlertas()` to get an isolated publisher. With a replaced `__new__`, the observers of one test go into the other tests.
2. Each `AlertaController()` registers a new `NotificadorUnidades` in the same publisher. Then each unit receives the same notification many times.

## Consequences

- The system uses one publisher. An observer registered in it receives the messages from all the screens.
- The constructor stays public. The single instance is guaranteed only through `instancia()`, which is the path of the system. A direct call to `PublicadorAlertas()` is for the tests.
- The single publisher stays in memory while the program runs. An observer stays registered until `cancelar_inscricao()`.
- The creation does not use a lock. The application uses only one thread (Tkinter).

## Location in the code

- `src/model/fiscalizacao/observador.py`: `PublicadorAlertas.instancia()`
- `src/controller/fiscalizacao/alerta_controller.py`: constructor of `AlertaController`
- `tests/test_fiscalizacao_alertas.py`: `TestPublicadorSingleton`, `test_varios_controllers_nao_duplicam_notificacoes`
