# ADR-F08: Singleton no publicador de alertas

**Status:** aceita

## Contexto

O `PublicadorAlertas` (ver [ADR-F02](ADR-F02-observer-notificacoes.pt-br.md)) guarda a lista de observadores que recebem os avisos de alerta.
Antes, cada `AlertaController` criava um publicador novo.
Na aplicação existe só um `AlertaController`, na aba Alertas, mas nada no código garantia isso.
Se outra tela criasse um `AlertaController`, ela teria outra lista de observadores.
Um observador inscrito em uma tela não receberia os avisos gerados na outra.

O `AlertaController` também aceita um publicador no construtor.
Os testes usam isso para trocar os observadores. O Singleton não pode impedir esses testes.

## Decisão

Usar o padrão **Singleton** no `PublicadorAlertas`, com acesso pela classe:

- `PublicadorAlertas.instancia()` devolve sempre o mesmo objeto. Ele é criado na primeira chamada.
- O `AlertaController` sem publicador no construtor usa `PublicadorAlertas.instancia()`.
- O `AlertaController` com publicador no construtor usa o publicador recebido. Os testes continuam iguais.
- O `NotificadorUnidades` é criado uma vez, no módulo do controller.
  Como `inscrever()` ignora observador repetido, criar vários controllers não duplica as notificações.

### Por que não bloquear o construtor

A forma clássica do Singleton em Python troca o `__new__` para que `PublicadorAlertas()` devolva sempre o mesmo objeto.
Essa forma foi rejeitada por dois motivos:

1. Os testes criam `PublicadorAlertas()` para ter um publicador isolado. Com o `__new__` trocado, os observadores de um teste passariam para os outros.
2. Cada `AlertaController()` inscreveria um `NotificadorUnidades` novo no mesmo publicador. Cada unidade receberia a mesma notificação várias vezes.

## Consequências

- O sistema usa um único publicador. Um observador inscrito nele recebe os avisos de qualquer tela.
- O construtor continua público. A garantia de instância única vale para quem usa `instancia()`, que é o caminho do sistema. Criar `PublicadorAlertas()` direto é para testes.
- O publicador único vive enquanto o programa roda. Um observador inscrito nele fica inscrito até `cancelar_inscricao()`.
- A criação não usa trava (lock). A aplicação usa uma só thread (Tkinter).

## Onde está no código

- `src/model/fiscalizacao/observador.py`: `PublicadorAlertas.instancia()`
- `src/controller/fiscalizacao/alerta_controller.py`: construtor do `AlertaController`
- `tests/test_fiscalizacao_alertas.py`: `TestPublicadorSingleton`, `test_varios_controllers_nao_duplicam_notificacoes`
