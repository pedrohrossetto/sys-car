# ADR-C01: Template Method in ModeloBase

**Status:** accepted

## Context

The models `Proprietario`, `PropriedadeRural` and `Localizacao` had the same code.
Each model opened the connection, made the SQL, ran it, did a commit and closed the connection.
Only the table name and the columns were different.

## Decision

Use the **Template Method** pattern in `src/model/base.py`:

- The class `ModeloBase` sets the fixed algorithm of `salvar()`, `deletar()`, `buscar_por_id()` and `listar_todos()`.
- Each subclass gives only the parts that change:
  - `TABELA`: the table name.
  - `COLUNAS`: the columns, without `id`.
  - The hooks `_valores()` and `_de_linha()`, if the default conversion is not applicable.
- Specific searches (`buscar_por_cpf`, `buscar_por_propriedade`) use the helpers `_buscar_um()` and `_buscar_varios()`.

## Consequences

- Each model has only its `SCHEMA`, its constructor and its specific searches.
- The public interface of the models did not change. Thus, the contract with Inspection stays the same.
- The constructor of a subclass must accept the names in `COLUNAS` and `id` as keyword arguments.

## Location in the code

- `src/model/base.py`: `ModeloBase`.
- `src/model/proprietario.py`, `src/model/propriedade_rural.py`, `src/model/localizacao.py`: subclasses.
