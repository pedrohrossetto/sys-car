# ADR-F03: Factory Method nas fontes de detecção

**Status:** aceita

## Contexto

Um alerta pode vir de um satélite ou de uma denúncia de usuário.
Cada origem preenche um campo diferente no registro (`satelite_id` ou `usuario_id`).
As regras também são diferentes: a denúncia de usuário exige pelo menos uma evidência, e o satélite não.

## Decisão

Usar o padrão **Factory Method**:

- `FonteDeteccao` (abstrata) declara o método fábrica `criar_registro(...)`.
- `Satelite` e `Usuario` herdam de `FonteDeteccao` e implementam `criar_registro()`.
  Cada um devolve um `RegistroDesmatamento` com a própria origem preenchida.
- `Satelite.detectar_desmatamento()` cria o registro sem exigir evidência.
- `Usuario.reportar_desmatamento()` exige pelo menos uma evidência e depois chama o método fábrica.
- O registro sempre nasce com status PENDENTE.

## Consequências

- O controller não decide qual coluna de origem preencher.
- Uma fonte nova (por exemplo, um drone) é uma subclasse nova de `FonteDeteccao`.
- O banco também garante a regra: o `CHECK` da tabela exige exatamente uma origem.

## Onde está no código

- `src/model/fiscalizacao/fonte.py`
- `src/model/fiscalizacao/satelite.py`, `src/model/fiscalizacao/usuario.py`
- `src/controller/fiscalizacao/alerta_controller.py`: `registrar_por_satelite()`, `registrar_por_usuario()`
