# ADR-C02: Strategy for the CPF and CNPJ validation

**Status:** accepted

## Context

An owner can be a natural person (PF, with a CPF) or a legal entity (PJ, with a CNPJ).
Each document has its own mask and check-digit rules.
Since 2026, the Brazilian tax office also gives CNPJ numbers with letters in the first 12 positions.

## Decision

Use the **Strategy** pattern in `src/model/documento.py`:

- `ValidadorDocumento` is the abstract interface. It has the methods `normalizar()` and `valido()`.
- `ValidadorCPF` and `ValidadorCNPJ` are the concrete strategies.
- The dictionary `VALIDADORES` connects each type to its strategy. `"PF"` uses `ValidadorCPF`. `"PJ"` uses `ValidadorCNPJ`.
- `ProprietarioController` selects the strategy from the type. It does not use `if/elif`.
- The database keeps only the valid characters, without the mask.
- `ValidadorCNPJ` accepts the alphanumeric CNPJ. In the calculation, each character has the value `ord(c) - 48`.

## Consequences

- For a new document type, make a new strategy and add it to `VALIDADORES`.
- A CPF that starts with zero stays as text. The zero is not lost.
- The alphanumeric CNPJ algorithm follows the rule from the tax office.
  The test uses the official example `12ABC34501DE35`.

## Location in the code

- `src/model/documento.py`: strategies and `VALIDADORES`.
- `src/controller/proprietario_controller.py`: method `_validar()`.
