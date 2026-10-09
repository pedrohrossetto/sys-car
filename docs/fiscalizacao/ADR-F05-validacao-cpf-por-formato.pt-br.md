# ADR-F05: CPF do usuário validado só pelo formato

**Status:** aceita

## Contexto

O usuário denunciante tem CPF. O Cadastro tem um validador completo de CPF, com dígito verificador.
A Fiscalização foi desenvolvida ao mesmo tempo e não podia depender de código que ainda não existia.

## Decisão

Validar o CPF do usuário só pelo formato: 11 dígitos, depois de remover pontos e hífen.
O banco guarda só os dígitos, e o CPF é único na tabela `usuarios`.

## Consequências

- Um CPF com 11 dígitos e dígito verificador errado é aceito para o usuário denunciante.
- Depois da integração, a melhoria é usar o `ValidadorCPF` do Cadastro (`src/model/documento.py`).
  Essa melhoria deve virar uma issue.

## Onde está no código

- `src/model/fiscalizacao/regras.py`: `normalizar_cpf()`, `cpf_formato_valido()`
- `src/controller/fiscalizacao/fonte_controller.py`: `_validar_usuario()`
