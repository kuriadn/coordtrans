# georef

Cassini-Soldner and UTM georeferencing library (NLIMS / Fayvad Geosolutions), merged into Fayvad Survey.

## Production modules

| Module | Role | Exposed via |
|--------|------|-------------|
| `affine.py` | 4-parameter affine least-squares | **Coordinate Transform** (sheet + custom modes) |
| `cassini_tables.py` | NLIMS log-table Cassini ↔ geographic | **CRS Transform** (`tables-*` presets) |
| `cassini_proj.py` | Panel central meridian, PROJ4 `lon_0` override | **CRS Transform** (custom Cassini + tables) |
| `utilities.py` | Backward-compatible re-exports | Internal / CLI |

## Archived

Legacy research scripts live in `georef/research/` (not imported by the web app).

## CLI

```bash
python -m georef.georef -i control_points.csv -v
```

CSV format: four columns per control pair (`from_x,from_y,to_x,to_y`), then two columns per point to transform.

## Django integration

| App | Uses georef for |
|-----|-----------------|
| `coordtrans` | Sheet affine + custom control-point affine (`coordtrans/compute.py`) |
| `crstrans` | Log-table Cassini presets (`crstrans/compute.transform_points_tables`) |
| `geocalc`, `traverse`, `areacalc` | Shared DMS via `fayvadgeo/survey_math.py` (not georef-specific) |

Django orchestration lives in `coordtrans/` and `crstrans/` — not in `fayvadgeo/georef.py` (removed).
