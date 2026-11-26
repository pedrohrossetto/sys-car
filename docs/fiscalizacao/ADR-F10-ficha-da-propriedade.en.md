# ADR-F10: Property record tab

**Status:** accepted. Updated after [ADR-C05](../cadastro/ADR-C05-area-da-propriedade.en.md) and [ADR-F14](ADR-F14-ponto-do-alerta-define-a-propriedade.en.md).

## Context

Foreign keys connect the tables of the system:

- a property belongs to one owner (N:1);
- a property has alerts, embargoes and declarations (1:N).

No screen showed these data together. To see the condition of a property, the user had to open many tabs.

Class 11 of the teaching plan asks for relations in the GUI, with one data access logic in the MVC pattern.

## Decision

Make the tab **Ficha da Propriedade** (property record). The user selects a property. Then the tab shows all the data that are connected to it.

- The tab is in the Fiscalização packages (`controller/fiscalizacao`, `view/fiscalizacao`), with `ORDEM = 90`.
  - Reason: the Fiscalização already uses the Cadastro. The Cadastro does not use the Fiscalização. The tab uses the two areas. Thus, it is on the side that already has this dependency.
- `FichaController.montar()` returns a `FichaPropriedade` object with all the data. The view does not use a model.
- The access to the Cadastro stays in `controller/fiscalizacao/propriedades.py` (see [ADR-F07](ADR-F07-integracao-por-contrato-de-plugin.en.md)).
  The contract has a new read function: `buscar_proprietario()`.
- `FichaPropriedade` calculates the **condition** (`situacao`) of the property:

  | Condition | Rule |
  |---|---|
  | EMBARGADA | There is an active embargo |
  | COM ALERTAS EM ABERTO | There is an alert whose state has `BLOQUEIA_CONFORMIDADE` (PENDENTE or CONFIRMADO) |
  | REGULAR | None of the cases above |

  The alert rule uses the State pattern (see [ADR-F01](ADR-F01-state-status-alerta.en.md)). It does not repeat the list of statuses.

## Consequences

- One screen shows the relations of the property and its area on a read-only map.
- The tab shows the data of the area: the center (centroid), the area in hectares and the number of vertices.
- The tab only reads data. It does not create, change or delete records.
- If the owner does not exist, the tab shows "não encontrado" (not found). It does not show an error.
- The tab imports `formatar_documento()` from the owners tab. Thus, the CPF and the CNPJ have the same format in the two tabs.

## Later changes

- [ADR-C05](../cadastro/ADR-C05-area-da-propriedade.en.md) replaced the location (1:1 table) with the area of the property (column `poligono`).
  The tab does not show the location now. It shows the area and the map.
- [ADR-F14](ADR-F14-ponto-do-alerta-define-a-propriedade.en.md) connects the alert to the property through the point on the map.
  The tab shows the alerts whose point is in the area.

## Location in the code

- `src/controller/fiscalizacao/ficha_controller.py`: `FichaController`, `FichaPropriedade`
- `src/controller/fiscalizacao/propriedades.py`: `buscar_proprietario()`
- `src/model/fiscalizacao/declaracao.py`: `listar_por_propriedade()`
- `src/view/fiscalizacao/ficha_aba.py`: `FichaAba`
- `tests/test_fiscalizacao_ficha.py`
