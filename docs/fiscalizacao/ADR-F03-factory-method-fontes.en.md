# ADR-F03: Factory Method for the detection sources

**Status:** replaced by [ADR-F11](ADR-F11-remocao-das-fontes-e-factory-na-declaracao.en.md)

## Context

An alert can come from a satellite or from a report of a user.
Each source fills a different field in the record (`satelite_id` or `usuario_id`).
The rules are also different:

- a report of a user requires a minimum of one evidence item;
- a satellite alert does not require evidence.

## Decision

Use the **Factory Method** pattern:

- `FonteDeteccao` (abstract) declares the factory method `criar_registro(...)`.
- `Satelite` and `Usuario` inherit from `FonteDeteccao` and implement `criar_registro()`.
  Each one returns a `RegistroDesmatamento` with its source filled.
- `Satelite.detectar_desmatamento()` creates the record without evidence.
- `Usuario.reportar_desmatamento()` requires a minimum of one evidence item. Then it calls the factory method.
- Each alert starts with the status PENDENTE.

## Consequences

- The controller does not select the source column.
- A new source (for example, a drone) is a new subclass of `FonteDeteccao`.
- The database also applies the rule: the `CHECK` of the table requires exactly one source.

## Location in the code

- `src/model/fiscalizacao/fonte.py`
- `src/model/fiscalizacao/satelite.py`, `src/model/fiscalizacao/usuario.py`
- `src/controller/fiscalizacao/alerta_controller.py`: `registrar_por_satelite()`, `registrar_por_usuario()`
