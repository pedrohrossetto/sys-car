# Fiscalização

A área de Fiscalização registra alertas de desmatamento, avisa as unidades competentes, controla embargos e emite declarações de conformidade ambiental.

## Decisões de projeto

| ADR | Assunto |
|---|---|
| [ADR-F01](ADR-F01-state-status-alerta.pt-br.md) | State no status do alerta |
| [ADR-F02](ADR-F02-observer-notificacoes.pt-br.md) | Observer nas notificações |
| [ADR-F03](ADR-F03-factory-method-fontes.pt-br.md) | Factory Method nas fontes de detecção |
| [ADR-F04](ADR-F04-coordenadas-embutidas-no-registro.pt-br.md) | Coordenadas embutidas no registro |
| [ADR-F05](ADR-F05-validacao-cpf-por-formato.pt-br.md) | CPF do usuário validado só pelo formato |
| [ADR-F06](ADR-F06-embargo-e-declaracao-como-entidades.pt-br.md) | Embargo e declaração como entidades |
| [ADR-F07](ADR-F07-integracao-por-contrato-de-plugin.pt-br.md) | Integração por contrato de plugin |

## Diagramas

- [Diagramas UML](diagramas.pt-br.md).

## Guia do usuário

- [Guia em Leitura Fácil](guia-leitura-facil.md).

## Testar sem a janela principal

A partir da pasta `src`:

```bash
python3 -m view.fiscalizacao._demo
```
