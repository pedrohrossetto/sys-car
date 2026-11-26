# Fiscalização

A área de Fiscalização registra alertas de desmatamento, avisa as unidades competentes, controla embargos e emite declarações de conformidade ambiental.

## Termos

Esta documentação usa estes termos com um significado fixo:

| Termo | Significado | Classe no código |
|---|---|---|
| Alerta | Ponto no mapa onde houve desmatamento. A propriedade é a que contém o ponto, ou nenhuma | `RegistroDesmatamento` |
| Unidade competente | Órgão que examina os alertas e aplica embargos | `UnidadeCompetente` |
| Notificação | Aviso que o sistema grava para uma unidade competente | `Notificacao` |
| Embargo | Bloqueio de uma propriedade por causa de um alerta confirmado | `Embargo` |
| Declaração | Documento que diz se a propriedade está em conformidade ambiental | `Declaracao` |
| Resultado da análise | Resultado do pedido de declaração: sem pendências ou com pendências | `ResultadoAnalise`, `SemPendencias`, `ComPendencias` |

## Decisões de projeto

| ADR | Assunto | EN |
|---|---|---|
| [ADR-F01](ADR-F01-state-status-alerta.pt-br.md) | State no status do alerta | [EN](ADR-F01-state-status-alerta.en.md) |
| [ADR-F02](ADR-F02-observer-notificacoes.pt-br.md) | Observer nas notificações | [EN](ADR-F02-observer-notificacoes.en.md) |
| [ADR-F03](ADR-F03-factory-method-fontes.pt-br.md) | Factory Method nas fontes de detecção (substituída pela ADR-F11) | [EN](ADR-F03-factory-method-fontes.en.md) |
| [ADR-F04](ADR-F04-coordenadas-embutidas-no-registro.pt-br.md) | Coordenadas embutidas no registro (substituída pela ADR-F14) | [EN](ADR-F04-coordenadas-embutidas-no-registro.en.md) |
| [ADR-F05](ADR-F05-validacao-cpf-por-formato.pt-br.md) | CPF do usuário validado só pelo formato (substituída pela ADR-F11) | [EN](ADR-F05-validacao-cpf-por-formato.en.md) |
| [ADR-F06](ADR-F06-embargo-e-declaracao-como-entidades.pt-br.md) | Embargo e declaração como entidades | [EN](ADR-F06-embargo-e-declaracao-como-entidades.en.md) |
| [ADR-F07](ADR-F07-integracao-por-contrato-de-plugin.pt-br.md) | Integração por contrato de plugin | [EN](ADR-F07-integracao-por-contrato-de-plugin.en.md) |
| [ADR-F08](ADR-F08-singleton-publicador-alertas.pt-br.md) | Singleton no publicador de alertas | [EN](ADR-F08-singleton-publicador-alertas.en.md) |
| [ADR-F09](ADR-F09-acesso-a-dados-unificado.pt-br.md) | Acesso a dados unificado no ModeloBase | [EN](ADR-F09-acesso-a-dados-unificado.en.md) |
| [ADR-F10](ADR-F10-ficha-da-propriedade.pt-br.md) | Ficha da propriedade | [EN](ADR-F10-ficha-da-propriedade.en.md) |
| [ADR-F11](ADR-F11-remocao-das-fontes-e-factory-na-declaracao.pt-br.md) | Remoção das fontes e da evidência; Factory Method na declaração | [EN](ADR-F11-remocao-das-fontes-e-factory-na-declaracao.en.md) |
| [ADR-F12](ADR-F12-crud-do-alerta.pt-br.md) | CRUD do alerta de desmatamento | [EN](ADR-F12-crud-do-alerta.en.md) |
| [ADR-F13](ADR-F13-operacoes-de-embargo-declaracao-e-notificacao.pt-br.md) | Operações de embargo, declaração e notificação | [EN](ADR-F13-operacoes-de-embargo-declaracao-e-notificacao.en.md) |
| [ADR-F14](ADR-F14-ponto-do-alerta-define-a-propriedade.pt-br.md) | O ponto do alerta define a propriedade | [EN](ADR-F14-ponto-do-alerta-define-a-propriedade.en.md) |

## Diagramas

- [Diagramas UML (pt-BR)](diagramas.pt-br.md) e [UML diagrams (EN)](diagramas.en.md).

## Guia do usuário

- [Guia em Leitura Fácil](guia-leitura-facil.md).

## Testar sem a janela principal

A partir da pasta `src`:

```bash
python3 -m view.fiscalizacao._demo
```
