# ADR-F06: Embargo and declaration as entities

**Status:** accepted

## Context

In the conceptual model, the embargo and the declaration are only methods:
`UNIDADE_COMPETENTE.embargarPropriedade()` and `PROPRIEDADE_RURAL.gerarDeclaracaoConformidade()`.
The system must keep the history of the embargoes: the unit, the date and the reason.
It must also keep the requested declarations.
A "situation" column in the property table changes a Cadastro table.

## Decision

Change the two methods into entities. Each entity has its own table:

- `embargos`: property, unit, the alert that is the cause, date, reason and `ativo`.
  - An embargo requires a CONFIRMADO alert of the same property.
  - A partial unique index in the database permits a maximum of one active embargo for each property.
  - To lift the embargo, the system sets `ativo` to 0. It does not delete the record.
- `declaracoes`: property, date, result (EMITIDA or NEGADA) and reason.
  - The result is NEGADA if the property has a PENDENTE alert, a CONFIRMADO alert or an active embargo.
  - The reason gives the list of the problems.
  - The system records all the requests, with the result EMITIDA or NEGADA.

## Consequences

- "Embargoed property" means "there is an embargo with `ativo = 1`".
- The full history is available for queries and for the `.txt` file of the declaration.
- The controller stops the deletion of a unit that applied an embargo.

## Location in the code

- `src/model/fiscalizacao/embargo.py`, `src/model/fiscalizacao/declaracao.py`
- `src/controller/fiscalizacao/conformidade_controller.py`
