# ADR-C02: Strategy na validação de CPF e CNPJ

**Status:** aceita

## Contexto

O proprietário pode ser pessoa física (PF, com CPF) ou pessoa jurídica (PJ, com CNPJ).
Cada documento tem regras próprias de máscara e de dígito verificador.
Desde 2026, a Receita Federal também emite CNPJ com letras nas 12 primeiras posições.

## Decisão

Usar o padrão **Strategy** em `src/model/documento.py`:

- `ValidadorDocumento` é a interface abstrata, com os métodos `normalizar()` e `valido()`.
- `ValidadorCPF` e `ValidadorCNPJ` são as estratégias concretas.
- O dicionário `VALIDADORES` liga o tipo à estratégia: `"PF"` usa `ValidadorCPF` e `"PJ"` usa `ValidadorCNPJ`.
- O `ProprietarioController` escolhe a estratégia pelo tipo, sem `if/elif`.
- O banco guarda só os caracteres válidos, sem máscara.
- O `ValidadorCNPJ` aceita o CNPJ alfanumérico. No cálculo, cada caractere vale `ord(c) - 48`.

## Consequências

- Para um tipo novo de documento, basta criar uma estratégia e incluí-la em `VALIDADORES`.
- O CPF que começa com zero é guardado como texto e não perde o zero.
- O algoritmo do CNPJ alfanumérico segue a regra publicada pela Receita.
  O teste usa o exemplo oficial `12ABC34501DE35`.

## Onde está no código

- `src/model/documento.py`: estratégias e `VALIDADORES`.
- `src/controller/proprietario_controller.py`: método `_validar()`.
