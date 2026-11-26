# ADR-F13: Operações de embargo, declaração e notificação

**Status:** aceita

## Contexto

A aula 08 pede as operações de atualizar e excluir pela GUI. A issue #5 pede essas operações onde elas fazem sentido
e, onde não fazem, uma decisão registrada num ADR.

Depois da [ADR-F12](ADR-F12-crud-do-alerta.pt-br.md), o alerta tem CRUD completo. A evidência saiu do sistema
([ADR-F11](ADR-F11-remocao-das-fontes-e-factory-na-declaracao.pt-br.md)). Faltavam 3 entidades:

| Entidade | Antes desta ADR |
|---|---|
| Embargo | criar, listar, levantar |
| Declaração | criar, listar |
| Notificação | criada automaticamente, listar, marcar como lida |

## Decisão

| Entidade | Atualizar | Excluir |
|---|---|---|
| Embargo | Só o **motivo**, pelo botão "Alterar motivo do selecionado" | **Não existe.** "Levantar embargo" faz esse papel |
| Declaração | **Não existe** | **Não existe** |
| Notificação | Só o status: "Marcar como lida" | **Não existe** |

### Embargo

- O motivo pode ser corrigido, num embargo ativo ou levantado.
- Propriedade, unidade, alerta e data **não** mudam. Eles registram quem embargou o quê e quando.
- Um embargo não é apagado. Levantar o embargo (`ativo = 0`) tira o bloqueio da propriedade e mantém o histórico.
  A ficha da propriedade e a aba de embargos continuam mostrando os embargos levantados.

### Declaração

- A declaração é um documento: ela registra o resultado da análise numa data. Ela pode ter sido salva em `.txt` e
  entregue a alguém.
- Mudar ou apagar a declaração faria o documento entregue diferir do sistema.
- Se a situação da propriedade muda, o proprietário pede uma declaração nova. A lista mostra todas, da mais nova para a
  mais antiga.

### Notificação

- A notificação é criada pelo sistema (Observer, [ADR-F02](ADR-F02-observer-notificacoes.pt-br.md)). Ela é o registro
  de que a unidade foi avisada.
- A única mudança é o status: ENVIADA para LIDA.
- Apagar uma notificação apagaria a prova do aviso. Por isso não existe exclusão.

## Exceção: exclusão em cascata

Os registros sem exclusão pela tela ainda são apagados em cascata pelo banco (`ON DELETE CASCADE`):

- apagar uma **propriedade** apaga os embargos, as declarações e as notificações dela;
- apagar um **alerta** apaga os embargos e as notificações dele (ADR-F12).

## Alternativas descartadas

- **Excluir embargos levantados:** limparia a lista, mas perderia o histórico da propriedade.
- **Excluir declaração pedida por engano:** o pedido não tem efeito sobre os outros dados. Uma declaração nova resolve.
- **Excluir notificações lidas:** limparia a caixa de entrada, mas perderia o registro dos avisos.

## Consequências

- A issue #5 está completa: cada entidade tem as operações que fazem sentido, e as que não existem estão justificadas aqui.
- As tabelas de embargos, declarações e notificações crescem sempre. Para um trabalho acadêmico, o volume é pequeno.

## Onde está no código

- `src/controller/fiscalizacao/conformidade_controller.py`: `alterar_motivo()`, `buscar_embargo()`
- `src/view/fiscalizacao/conformidade_aba.py`: botão "Alterar motivo do selecionado"
- `tests/test_fiscalizacao_conformidade.py`: `test_alterar_motivo_do_embargo`
