# ADR-C05: Property area as a mandatory polygon

**Status:** accepted

## Context

`Localizacao` was a 1:1 table with the property. It kept a centre point that the user typed (latitude and longitude),
the altitude and an **optional** polygon as text.

Problems:

- The centre point could be outside the polygon, because the user typed them separately.
- Without a polygon, the system cannot find if a deforestation alert is inside the property.
- The "Localizações" tab was one more screen for data that belongs to the property.

The team decided to define the geography on a map: each property has an **area** that the user draws with clicks.

## Decision

1. `Localizacao` (table `localizacoes`, controller and tab) is removed. The altitude is also removed.
2. The property gets the column `poligono`: the area, as the text `lat,lon;lat,lon;...` (`model/coordenadas.py`).
   - In the database, the column accepts NULL. The contract with Fiscalização requires that new columns accept NULL.
   - `PropriedadeRuralController` requires the area. Without an area, it does not save the property.
3. The class `Poligono` (`model/geometria.py`) contains the logic. It is a **value object**: it has no table.
   - Validation: minimum 3 vertices, latitude and longitude ranges, area not zero, and sides that do not cross.
   - `centroide()`: the centre of the area. It replaces the latitude and longitude of the old Localização.
   - `area_ha()`: the area in hectares. The vertices are projected to metres around the mean latitude.
   - `contem(lat, lon)`: true if the point is in the area. A point on the border is in the area.
   - `sobrepoe(outro)`: true if two areas have a common interior. Two areas that touch on a side or a vertex do not overlap.
4. **Two properties must not overlap.** The controller compares the new area with the other areas (on update, it
   ignores the same property). Thus, each point on the map belongs to a maximum of one property.
5. `PropriedadeRural` gives `area`, `centroide`, `area_ha` and `contem()`. It calculates them from `poligono`.

## Rejected alternatives

- **Keep the table `localizacoes` without a tab:** one more table and one more join for data of the property.
- **Typed centre and optional area:** the centre could be outside the area, and alerts cannot find a property without an area.
- **Allow overlap (the oldest property wins):** one point could belong to two properties.

## Consequences

- The centre of the property is always in the area.
- An alert can find its property from its point (see ADR-F14 of Fiscalização).
- A property saved directly in the database without an area has `area`, `centroide` and `area_ha` equal to None.
  It contains no point.
- The program finds an old database (without the column `poligono`) when it starts. It tells the user to delete `data/syscar.db`.

## Where it is in the code

- `src/model/geometria.py`: `Poligono`
- `src/model/propriedade_rural.py`: column `poligono`, `area`, `centroide`, `area_ha`, `contem()`, `schema_desatualizado()`
- `src/controller/propriedade_rural_controller.py`: `_validar_area()`, `listar_areas()`
- `tests/test_cadastro_geometria.py`, `tests/test_cadastro_propriedade_area.py`
