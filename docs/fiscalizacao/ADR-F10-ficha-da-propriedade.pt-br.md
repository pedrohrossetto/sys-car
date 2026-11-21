# ADR-F10: Ficha da propriedade

**Status:** aceita

## Contexto

As tabelas do sistema estão ligadas por chaves estrangeiras:

- uma propriedade pertence a um proprietário (N:1);
- uma propriedade tem uma localização (1:1);
- uma propriedade tem alertas, embargos e declarações (1:N).

Nenhuma tela mostrava esses dados juntos. Para ver a situação de uma propriedade, o usuário precisava abrir 5 abas.

A aula 11 do plano de ensino pede relacionamentos na GUI, com acesso a dados unificado no padrão MVC.

## Decisão

Criar a aba **Ficha da Propriedade**. O usuário escolhe uma propriedade, e a aba mostra todos os dados ligados a ela.

- A ficha fica no pacote da Fiscalização (`controller/fiscalizacao`, `view/fiscalizacao`), com `ORDEM = 90`.
  - Motivo: a Fiscalização já depende do Cadastro. O Cadastro não depende da Fiscalização. A ficha usa as duas áreas, então ela fica do lado que já tem essa dependência.
- O `FichaController.montar()` devolve um objeto `FichaPropriedade` com todos os dados. A view não acessa nenhum model.
- O acesso ao Cadastro continua concentrado em `controller/fiscalizacao/propriedades.py` (ver [ADR-F07](ADR-F07-integracao-por-contrato-de-plugin.pt-br.md)).
  O contrato ganhou duas leituras: `buscar_proprietario()` e `buscar_localizacao()`.
- A `FichaPropriedade` calcula a **situação** da propriedade:

  | Situação | Regra |
  |---|---|
  | EMBARGADA | Existe um embargo ativo |
  | COM ALERTAS EM ABERTO | Existe um alerta cujo estado tem `BLOQUEIA_CONFORMIDADE` (PENDENTE ou CONFIRMADO) |
  | REGULAR | Nenhum dos casos acima |

  A regra dos alertas usa o State (ver [ADR-F01](ADR-F01-state-status-alerta.pt-br.md)). Ela não repete a lista de status.

## Consequências

- Uma tela mostra os 5 relacionamentos da propriedade.
- A ficha só lê dados. Ela não cria, não altera e não apaga registros.
- Se o proprietário ou a localização não existe, a ficha mostra "não encontrado" ou "não cadastrada". Ela não mostra erro.
- A aba "Ficha da Propriedade" importa `formatar_documento()` da aba de proprietários. Assim, o CPF e o CNPJ aparecem com a mesma máscara nas duas abas.

## Onde está no código

- `src/controller/fiscalizacao/ficha_controller.py`: `FichaController`, `FichaPropriedade`
- `src/controller/fiscalizacao/propriedades.py`: `buscar_proprietario()`, `buscar_localizacao()`
- `src/model/fiscalizacao/declaracao.py`: `listar_por_propriedade()`
- `src/view/fiscalizacao/ficha_aba.py`: `FichaAba`
- `tests/test_fiscalizacao_ficha.py`
