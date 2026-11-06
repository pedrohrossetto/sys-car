# ADR-F02: Observer nas notificações

**Status:** aceita

## Contexto

O sistema precisa avisar as unidades competentes quando cria um alerta ou muda o status de um alerta.
O código que registra o alerta não deve conhecer os detalhes de quem recebe o aviso.

## Decisão

Usar o padrão **Observer**:

- `ObservadorAlerta` (abstrato) declara `atualizar(registro, evento)`.
- `PublicadorAlertas` guarda a lista de observadores e oferece `inscrever()`, `cancelar_inscricao()` e `notificar()`.
- `NotificadorUnidades` é o observador concreto. Ele cria uma `Notificacao` para **cada** unidade competente cadastrada.
- O `AlertaController` chama `publicador.notificar()` depois de criar um alerta e depois de cada mudança de status.
- O `AlertaController` aceita outro publicador no construtor. Os testes usam isso para trocar os observadores.

## Consequências

- Um aviso novo (por exemplo, por e-mail) é um observador novo. O controller não muda.
- Se não há unidades cadastradas, o sistema não cria notificações. Isso não causa erro.
- A notificação é só uma linha no banco. O sistema não envia mensagens reais.

## Onde está no código

- `src/model/fiscalizacao/observador.py`
- `src/model/fiscalizacao/notificador.py`
- `src/controller/fiscalizacao/alerta_controller.py`
