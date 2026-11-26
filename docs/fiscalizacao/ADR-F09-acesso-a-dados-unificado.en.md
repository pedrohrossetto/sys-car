# ADR-F09: One data access method in ModeloBase

**Status:** accepted. Replaces item 5 of [ADR-F07](ADR-F07-integracao-por-contrato-de-plugin.en.md).

## Context

The system had two methods to access the database:

- The Cadastro models inherited from `ModeloBase` (see [ADR-C01](../cadastro/ADR-C01-template-method-modelo-base.en.md)).
- The 8 Fiscalização models used `conexao.py`. Each model had its own SQL for INSERT, UPDATE, DELETE and SELECT.

The team developed the two areas at the same time. Thus, the Fiscalização could not use `ModeloBase`, because it did not exist yet.

Classes 09 and 10 of the teaching plan ask for one data access logic, connected to the GUI in the MVC pattern.

## Decision

All the models of the system inherit from `ModeloBase`:

- The 8 Fiscalização models declare `TABELA` and `COLUNAS`, as the Cadastro models do.
  - `Satelite`, `Usuario`, `UnidadeCompetente`, `RegistroDesmatamento`
  - `Evidencia`, `Notificacao`, `Embargo`, `Declaracao`
- The team removed the file `conexao.py`.
- The specific queries use the helpers of `ModeloBase`. They do not have full SQL statements.

The Fiscalização needed two functions that `ModeloBase` did not have. Now `ModeloBase` has these functions:

| Function | Use in the Fiscalização |
|---|---|
| `_buscar_varios(..., ordem=...)` | Show the embargoes, declarations and notifications from the newest to the oldest |
| `_existe(condicao, parametros)` | Find if a unit applied an embargo and if a source created an alert |

The default value of `ordem` is `id`. Thus, the Cadastro models continue to show the rows in ascending order.

## Consequences

- The system has only one method to access the database. A correction in `ModeloBase` applies to the 11 models.
- The names of the public methods did not change. The controllers and the views did not change.
- `Notificacao` and `Embargo` now write all the columns in the UPDATE. Before, they wrote only `status` and `ativo`.
  The result in the database is the same, because the object comes from the database before the change.
- Now all the models have `deletar()`. This prepares issue #5 (full CRUD).
- The `__init__.py` of the package still opens a connection. It only runs the `SCHEMA` constants before the integration (tests and `_demo.py`). It does not read or write records.

## Later changes

[ADR-F11](ADR-F11-remocao-das-fontes-e-factory-na-declaracao.en.md) removed `Satelite`, `Usuario` and `Evidencia`.
[ADR-C05](../cadastro/ADR-C05-area-da-propriedade.en.md) removed `Localizacao` from the Cadastro.
The decision of this ADR is still correct: now the 7 models of the system inherit from `ModeloBase`.

| Area | Models |
|---|---|
| Cadastro | `Proprietario`, `PropriedadeRural` |
| Fiscalização | `UnidadeCompetente`, `RegistroDesmatamento`, `Notificacao`, `Embargo`, `Declaracao` |

Now the helper `_existe()` only finds if a unit applied an embargo (`Embargo.existe_da_unidade()`).

## Location in the code

- `src/model/base.py`: `_buscar_varios()` with `ordem`, and `_existe()`
- `src/model/fiscalizacao/*.py`: the Fiscalização models
- `tests/test_fiscalizacao_acesso_unificado.py`
