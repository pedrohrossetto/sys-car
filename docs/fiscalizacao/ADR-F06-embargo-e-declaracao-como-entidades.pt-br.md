# ADR-F06: Embargo e declaração como entidades

**Status:** aceita

## Contexto

No modelo conceitual, o embargo e a declaração aparecem só como métodos:
`UNIDADE_COMPETENTE.embargarPropriedade()` e `PROPRIEDADE_RURAL.gerarDeclaracaoConformidade()`.
O sistema precisa guardar o histórico: quem embargou, quando, por quê, e quais declarações foram pedidas.
Uma coluna "situação" na tabela de propriedades mudaria uma tabela do Cadastro.

## Decisão

Materializar os dois métodos como entidades, com tabelas próprias:

- `embargos`: propriedade, unidade, alerta que justificou, data, motivo e `ativo`.
  - Embargar exige um alerta CONFIRMADO da própria propriedade.
  - Um índice único parcial garante no banco no máximo um embargo ativo por propriedade.
  - Levantar o embargo muda `ativo` para 0. O registro não é apagado.
- `declaracoes`: propriedade, data, resultado (EMITIDA ou NEGADA) e motivo.
  - É NEGADA se houver alerta PENDENTE ou CONFIRMADO ou um embargo ativo. O motivo lista os impedimentos.
  - Todo pedido é gravado, emitido ou negado.

## Consequências

- "Propriedade embargada" significa "existe um embargo com `ativo = 1`".
- O histórico completo fica disponível para consulta e para o arquivo `.txt` da declaração.
- Excluir uma unidade que já aplicou embargo é bloqueado pelo controller.

## Onde está no código

- `src/model/fiscalizacao/embargo.py`, `src/model/fiscalizacao/declaracao.py`
- `src/controller/fiscalizacao/conformidade_controller.py`
