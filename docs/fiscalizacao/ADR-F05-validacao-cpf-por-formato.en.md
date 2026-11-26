# ADR-F05: User CPF checked only by its format

**Status:** replaced by [ADR-F11](ADR-F11-remocao-das-fontes-e-factory-na-declaracao.en.md)

## Context

The user that reports deforestation has a CPF. The Cadastro has a full CPF validator, with the check digits.
The team developed the Fiscalização at the same time as the Cadastro.
Thus, the Fiscalização could not use code that did not exist yet.

## Decision

Check the CPF of the user only by its format: 11 digits, after the system removes the dots and the hyphen.
The database keeps only the digits.
The CPF is unique in the table `usuarios`.

## Consequences

- For the user that reports deforestation, the system accepts a CPF with 11 digits and incorrect check digits.
- After the integration, the improvement is to use the `ValidadorCPF` of the Cadastro (`src/model/documento.py`).
  This improvement must become an issue.

## Location in the code

- `src/model/fiscalizacao/regras.py`: `normalizar_cpf()`, `cpf_formato_valido()`
- `src/controller/fiscalizacao/fonte_controller.py`: `_validar_usuario()`
