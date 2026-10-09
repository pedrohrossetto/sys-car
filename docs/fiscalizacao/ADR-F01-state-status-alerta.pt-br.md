# ADR-F01: State no status do alerta

**Status:** aceita

## Contexto

Um alerta de desmatamento passa pelos status PENDENTE, CONFIRMADO, RESOLVIDO e CANCELADO.
Nem toda mudança é permitida. Um alerta PENDENTE não pode ir direto para RESOLVIDO.
Com `if/elif` espalhados, cada tela e cada controller teria de repetir as regras.

## Decisão

Usar o padrão **State** em `src/model/fiscalizacao/status.py`:

- `StatusAlerta` é o enum dos quatro status.
- Cada status tem uma classe de estado: `Pendente`, `Confirmado`, `Resolvido` e `Cancelado`.
- Cada estado declara `PROXIMOS`, os estados para onde ele pode ir:
  - PENDENTE → CONFIRMADO ou CANCELADO;
  - CONFIRMADO → RESOLVIDO;
  - RESOLVIDO e CANCELADO são finais.
- `RegistroDesmatamento.mudar_status()` delega a mudança ao estado atual (`estado.ir_para()`).
  Uma transição inválida levanta `TransicaoInvalida`. O controller devolve `(None, "mensagem")`.
- Cada estado também declara `BLOQUEIA_CONFORMIDADE`. PENDENTE e CONFIRMADO impedem a declaração.

## Consequências

- As regras de transição ficam em um arquivo só.
- O menu de contexto da aba Alertas mostra só as transições permitidas (`transicoes_possiveis()`).
- A declaração de conformidade não repete a lista de status que bloqueiam.

## Onde está no código

- `src/model/fiscalizacao/status.py`
- `src/model/fiscalizacao/registro_desmatamento.py`: `mudar_status()`
- `src/controller/fiscalizacao/alerta_controller.py`: `mudar_status()`, `transicoes_possiveis()`
