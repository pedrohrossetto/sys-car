# ADR-F06: Embargo e declaração como entidades

**Status:** aceita

## Contexto

No modelo conceitual, o embargo e a declaração aparecem só como métodos:
`UNIDADE_COMPETENTE.embargarPropriedade()` e `PROPRIEDADE_RURAL.gerarDeclaracaoConformidade()`.
O sistema precisa guardar o histórico dos embargos: quem embargou, quando e por quê.
Ele também precisa guardar as declarações pedidas.
Uma coluna "situação" na tabela de propriedades mudaria uma tabela do Cadastro.

## Decisão

Transformar os dois métodos em entidades, cada uma com tabela própria:

- `embargos`: propriedade, unidade, alerta que justificou, data, motivo e `ativo`.
  - Embargar exige um alerta CONFIRMADO da própria propriedade.
  - Um índice único parcial garante no banco no máximo um embargo ativo por propriedade.
  - Levantar o embargo muda `ativo` para 0. O registro não é apagado.
- `declaracoes`: propriedade, data, resultado (EMITIDA ou NEGADA) e motivo.
  - O resultado é NEGADA se a propriedade tem um alerta PENDENTE, um alerta CONFIRMADO ou um embargo ativo.
  - O motivo lista os impedimentos.
  - O sistema grava todos os pedidos, com resultado EMITIDA ou NEGADA.

## Consequências

- "Propriedade embargada" significa "existe um embargo com `ativo = 1`".
- O histórico completo fica disponível para consulta e para o arquivo `.txt` da declaração.
- O controller bloqueia a exclusão de uma unidade que já aplicou um embargo.

## Onde está no código

- `src/model/fiscalizacao/embargo.py`, `src/model/fiscalizacao/declaracao.py`
- `src/controller/fiscalizacao/conformidade_controller.py`
