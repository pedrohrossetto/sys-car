# ADR-F04: Coordinates in the alert record

**Status:** replaced by [ADR-F14](ADR-F14-ponto-do-alerta-define-a-propriedade.en.md)

## Context

In the conceptual model, `REGISTRO_DESMATAMENTO` contains a `LOCALIZACAO`.
In the Cadastro implementation, the table `localizacoes` has `propriedade_id UNIQUE NOT NULL`:
each location belongs to one property, in a 1:1 relation.
To use this table for the alerts, the team must change a Cadastro table.
This also makes the two areas dependent on each other.

## Decision

The record keeps its own coordinates: the columns `latitude` and `longitude` are in the table `registros_desmatamento`.
The composition relation stays: the system creates and deletes the coordinates together with the alert.
The alert also points to the property (`propriedade_id`), with `ON DELETE CASCADE`.

## Consequences

- The Fiscalização does not change a Cadastro table.
- The database checks the ranges: latitude from -90 to 90 and longitude from -180 to 180.
- The alert keeps a point, not a polygon.
- The system does not check if the point is in the polygon of the property. This check is out of scope.

## Location in the code

- `src/model/fiscalizacao/registro_desmatamento.py`: `SCHEMA`
