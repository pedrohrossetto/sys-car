# ADR-F14: The point of the alert sets the property

**Status:** accepted. Replaces [ADR-F04](ADR-F04-coordenadas-embutidas-no-registro.en.md) and changes
[ADR-F12](ADR-F12-crud-do-alerta.en.md).

## Context

ADR-F04 kept the coordinates in the alert. But the user selected the property in a list, separately from the point.
ADR-F04 did not check if the point is in the area of the property. This check was out of scope.

Now each property has an area, and the areas do not overlap ([ADR-C05](../cadastro/ADR-C05-area-da-propriedade.en.md)).
The user marks the alert with a click on the map ([ADR-002](../decisoes/ADR-002-mapa-em-canvas.en.md)).

## Decision

1. The system creates the alert with only the point (`AlertaController.criar(descricao, latitude, longitude, data)`).
2. The property of the alert is **the property that contains the point**: `propriedade_no_ponto()` in the contract with the Cadastro
   (`controller/fiscalizacao/propriedades.py`, see ADR-F07). The areas do not overlap. Thus, there is a maximum of one property.
3. If the point is not in an area, the alert has **no property** (`propriedade_id` NULL).
   - The alert shows on the map and in the list ("fora de propriedade cadastrada", outside a registered property). The units receive a notification.
   - The alert does not stop a declaration and does not permit an embargo. An embargo still requires a CONFIRMADO alert of the property.
4. The system records the property when it creates the alert. **The point does not change after this**: the update changes only the description and the date.
   To correct a point, the user deletes the alert and creates a new alert. This changes ADR-F12, which permitted changes to the coordinates.
5. The deletion of a property does **not** delete its alerts: `ON DELETE SET NULL`. The deforestation occurred. Thus, the alert
   stays on the map, without a property. The database still deletes the embargoes and the declarations of the property in cascade.

## Rejected alternatives

- **Calculate the property in each query (no column):** the property of an alert changes when the user edits an area.
  Then an embargo can be connected to an alert of a different property.
- **Movable point, with a new calculation of the property:** the same problem with the embargoes.
- **Delete the alerts with the property:** this deletes the record of a deforestation that occurred.

## Accepted risks

- A change to the area of a property does **not** connect the old alerts again. An alert can stay connected to a property
  whose new area does not contain the point. An alert can also have no property, but its point is in an area that the user drew later.
- The program finds an old database (property without `poligono`) when it starts. Then it tells the user to delete `data/syscar.db`.

## Location in the code

- `src/model/fiscalizacao/registro_desmatamento.py`: optional `propriedade_id`, `ON DELETE SET NULL`
- `src/controller/fiscalizacao/propriedades.py`: `propriedade_no_ponto()`, `listar_areas()`
- `src/controller/fiscalizacao/alerta_controller.py`: `criar()`, `atualizar()`, `descrever_local()`
- `src/view/fiscalizacao/alertas_aba.py`: click on the map
- `tests/test_fiscalizacao_alertas.py`, `tests/test_fiscalizacao_conformidade.py`
