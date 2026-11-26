# ADR-F12: CRUD do alerta de desmatamento

**Status:** aceita, alterada pela [ADR-F14](ADR-F14-ponto-do-alerta-define-a-propriedade.pt-br.md) (as coordenadas não mudam mais no update)

## Contexto

A aula 08 pede as 4 operações (criar, listar, atualizar e excluir) pela GUI.
O alerta só podia ser criado e listado. A única alteração possível era a mudança de status pelo State (ADR-F01).

## Decisão

O `AlertaController` tem o CRUD completo, como os outros controllers. O model continua herdando o acesso a dados do
`ModeloBase` (Template Method, ADR-F09).

| Operação | Método | Regra |
|---|---|---|
| Criar | `criar(propriedade_id, descricao, latitude, longitude, data=None)` | Todo alerta começa PENDENTE. As unidades recebem uma notificação (Observer). |
| Ler | `buscar_por_id(id)`, `listar(incluir_finalizados=True)` | |
| Atualizar | `atualizar(id, descricao, latitude, longitude, data=None)` | Muda só a descrição, a data e as coordenadas, em qualquer status. Não gera notificação. |
| Excluir | `excluir(id)` | Apaga o alerta. O banco apaga em cascata as notificações e os **embargos** do alerta. |

- O **status** não muda pelo `atualizar()`. Ele muda só por `mudar_status()`, que respeita as transições do State.
- A **propriedade** do alerta não muda. Os embargos apontam para o alerta e para a propriedade, e os dois têm de continuar coerentes.
- Na aba Alertas, o duplo clique (ou Enter) carrega o alerta no formulário. Salvar cria ou atualiza. Excluir pede
  confirmação e avisa que os embargos e as notificações do alerta também serão apagados.

## Alternativas descartadas

- **Bloquear a exclusão de alerta com embargo:** mais seguro, mas o grupo escolheu a exclusão livre.
- **Permitir excluir só alertas PENDENTES ou CANCELADOS:** idem.
- **Métodos de CRUD explícitos no model:** repetiriam o `ModeloBase` e enfraqueceriam o Template Method.

## Risco aceito

Excluir um alerta CONFIRMADO apaga o embargo que ele gerou. A propriedade pode deixar de estar embargada sem que uma
unidade levante o embargo. A confirmação na tela avisa sobre isso.

## Onde está no código

- `src/controller/fiscalizacao/alerta_controller.py`: `criar()`, `atualizar()`, `excluir()`
- `src/view/fiscalizacao/alertas_aba.py`: formulário com Salvar, Excluir e Limpar
- `tests/test_fiscalizacao_alertas.py`
