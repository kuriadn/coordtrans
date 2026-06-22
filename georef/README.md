# georef

Cassini-Soldner and UTM georeferencing library (NLIMS Directorate, National Land Commission).

Merged into [Fayvad Survey](https://github.com/kuriadn/coordtrans) as the `georef` Python package.

## Modules

| Module | Purpose |
|--------|---------|
| `utilities.py` | Affine transform core (`genCoeffMatrix`, `compute`), Cassini helpers |
| `georef.py` | CLI affine transformation from CSV control points |
| `cassini.py` | Cassini-Soldner projection utilities |
| `cassproc.py` | Cassini processing pipeline |
| `cass_utm.py` | Cassini ↔ UTM conversion |
| `cassproj4.py` | PROJ4 string helpers |
| `casstables.py` | Cassini table data |
| `anglemanip.py` | Angle conversion utilities |

## CLI usage

From the project root:

```bash
python -m georef.georef -i control_points.csv
python -m georef.georef -v -i control_points.csv -o output.csv
```

Input CSV: four columns per control point (`from_x, from_y, to_x, to_y`) for fitting, or two columns (`x, y`) for points to transform.

## Django integration

The web coordinate transform tool (`coordtrans`) uses this library via `fayvadgeo/georef.py`, which imports `genCoeffMatrix` and `compute` from `georef.utilities`.
