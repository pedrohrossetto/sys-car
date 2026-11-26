# ADR-F11: Removal of the sources and the evidence, with the Factory Method in the declaration

**Status:** accepted. Replaces [ADR-F03](ADR-F03-factory-method-fontes.en.md) and [ADR-F05](ADR-F05-validacao-cpf-por-formato.en.md).

## Context

The satellite, the reporting user and the evidence only tell where an alert came from.
They are not part of the main flow of the system: registration, alert, embargo and declaration.
But they used 3 tables, the Fontes tab, the `FonteController`, the CPF and e-mail rules and many tests.

The team decided to make the scope smaller and to remove these 3 entities.

Problem: the only Factory Method of the system was in the sources (`FonteDeteccao`, see ADR-F03).
Class 02 of the teaching plan asks for creational patterns: Factory and Singleton.
Without the sources, the Factory Method must go to a different location.

## Decision

1. Remove `Satelite`, `Usuario`, `Evidencia` and `FonteDeteccao`, the Fontes tab and the `FonteController`.
   - The table `registros_desmatamento` loses the columns `satelite_id` and `usuario_id` and the source `CHECK`.
   - The CPF and e-mail rules of the Fiscalização (ADR-F05) are also removed. Only the reporting user used them.
2. Put the **Factory Method** in the creation of the **compliance declaration**:
   - `ResultadoAnalise` (abstract) declares the factory method `criar_declaracao(propriedade_id, data)`.
   - `SemPendencias.criar_declaracao()` returns an EMITIDA (issued) declaration.
   - `ComPendencias(impedimentos).criar_declaracao()` returns a NEGADA (refused) declaration. The reason gives the problems.
   - `analisar(impedimentos)` selects the concrete result.
   - `ConformidadeController.solicitar_declaracao()` makes the list of problems and calls
     `analisar(impedimentos).criar_declaracao(...)`. The `if/else` is not in the controller now.
3. An old database still has the column `satelite_id`. The program finds this (`RegistroDesmatamento.schema_desatualizado()`).
   Then it tells the user to delete the file `data/syscar.db`, as it already does for the owner.

## Rejected alternatives

- **Keep the Factory Method in the sources, with a column `origem` in the alert:** without the evidence, the two factories
  only change the value of one column. The pattern is then artificial.
- **Factory Method for the PF/PJ owner:** the Strategy of the document (ADR-C02) already does this.
- **Remove the Factory Method and not replace it:** then class 02 has no Factory pattern.

## Consequences

- Less code and fewer screens: 3 tables, 1 tab and 1 controller less.
- The system does not keep the source of the alert or the evidence now. The description of the alert can give the source.
- Each result has a different creation rule for the declaration. A new result (for example, "issued with conditions")
  is a new subclass of `ResultadoAnalise`.
- The text of the reason of a refused declaration did not change.

## Location in the code

- `src/model/fiscalizacao/resultado_analise.py`: `ResultadoAnalise`, `SemPendencias`, `ComPendencias`, `analisar()`
- `src/controller/fiscalizacao/conformidade_controller.py`: `solicitar_declaracao()`
- `src/model/fiscalizacao/registro_desmatamento.py`: `schema_desatualizado()`
- `src/model/base.py`: `colunas_no_banco()`
- `tests/test_fiscalizacao_conformidade.py`: `TestFactoryMethodDaDeclaracao`
