# ADR-002: Own map in a Canvas

**Status:** accepted

## Context

The user defines the property area (ADR-C05) and the alert point (ADR-F14) with clicks on a map.
The project uses only the Python standard library (Tkinter and SQLite). There is no `pip install`.

## Decision

Draw the map in a `tk.Canvas`, without an external dependency.

- `view/projecao.py`, class `Projecao`: changes latitude/longitude to pixels and pixels to latitude/longitude.
  - Equirectangular projection. One degree of latitude always has the same height. One degree of longitude is made
    narrower by `cos(reference latitude)`. Thus, areas do not look stretched.
  - The reference latitude changes only when the map fits the content. Move and zoom do not change the shapes.
  - Zoom keeps the point under the cursor at the same position. The scale has a minimum and a maximum.
  - The grid selects the step (from 10° to 0.00001°) so that the lines are a minimum of 70 pixels apart.
  - The module **does not import tkinter**. The tests run on computers without Tk.
- `view/mapa.py`:
  - `MapaCanvas`: grid with labels, areas (polygons), points (colour from the alert status) and the area in edit.
    Mouse wheel: zoom. Drag with the left button: move. Click without drag: `ao_clicar(lat, lon)`.
    Button "Enquadrar tudo" (fit all). The coordinates under the cursor show below the map.
  - `EditorArea`: draws the area of a property. Each click is a vertex. Buttons "Desfazer vértice" (undo vertex) and
    "Limpar área" (clear area). It shows the vertices, the area (ha) and the centre, or the validation error of `Poligono`.
- The map is on the tabs Propriedades (draw the area), Alertas (mark the point) and Ficha da Propriedade (read only).

## Rejected alternatives

- **`tkintermapview`** (OpenStreetMap map in Tkinter): it has a real background image, but it is the first dependency
  of the project (`pip install`) and it needs the internet to load the map. During the presentation, without the
  internet, the map would be empty.

## Consequences

- The program has no dependencies and it operates without the internet.
- The map has no background image (roads, rivers, satellite). It is a coordinate plane with a grid.
- The equirectangular projection changes the shape of very large areas or areas near the poles. For rural
  properties, the difference is small.
- On macOS, Tk ignores `stipple`: the fill of the areas is solid, not transparent.

## Where it is in the code

- `src/view/projecao.py`: `Projecao`
- `src/view/mapa.py`: `MapaCanvas`, `EditorArea`
- `tests/test_view_projecao.py`
