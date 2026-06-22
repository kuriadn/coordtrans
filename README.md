# Fayvad Survey (survey.fayvad.com)

Online survey toolkit by **Fayvad Geosolutions** — a collection of field-ready calculators and converters for land survey professionals. The first live tool is **Coordinate Transform** (Cassini-Soldner ↔ UTM).

## Stack (LTS)

| Component | Version | Support |
|-----------|---------|---------|
| Django | 5.2 LTS | Security fixes until April 2028 |
| Python | 3.10–3.13 | Required by Django 5.2 |
| PostgreSQL + PostGIS | 14+ recommended | Database |
| GDAL | System package | Django GIS backend |
| Leaflet | 1.9.x | Map viewer (CDN or vendored) |
| pyproj | 3.7.x | Coordinate reprojection for maps |

## Requirements

- Python 3.10–3.13
- PostgreSQL with PostGIS extension
- GDAL development libraries

## Configuration

| Variable | Purpose |
|----------|---------|
| `SECRET_KEY` | Django secret key |
| `DATABASE_URL` | PostgreSQL connection string |
| `DEBUG` | Enable development mode |
| `ALLOWED_HOSTS` | Comma-separated hosts (production) |
| `CSRF_TRUSTED_ORIGINS` | HTTPS origins for CSRF (production) |
| `GOOGLE_MAPS_API_KEY` | Optional Google Maps basemap |

Production settings module: `fayvadgeo.settings.production`

Site identity (`SITE_NAME`, `SITE_DOMAIN`) and the tools catalogue live in `fayvadgeo/settings/base.py` and `fayvadgeo/context_processors.py`.

Survey tools are **public** (no login). Staff sign in at `/login/` or `/admin/` to manage sheet control data.

## Survey tools

| Tool | Status | URL |
|------|--------|-----|
| Coordinate Transform (sheet) | Live | `/coord_trans/enter_points/` |
| CRS Transform (PROJ) | Live | `/crs/` |
| Traverse Adjustment | Live | `/traverse/` |
| Area & Perimeter | Live | `/area/` |
| Bearing & Distance | Live | `/bearing/` |

Default CRS definitions: `MAP_CASSINI_PROJ4` and `MAP_UTM_EPSG` in `fayvadgeo/settings/base.py`.

## georef library

The [kuriadn/georef](https://github.com/kuriadn/georef) library is merged under `georef/` and wired into existing tools (no duplicate apps):

| Capability | Where users access it |
|------------|----------------------|
| Sheet affine transform | `/coord_trans/` → **Cadastral sheet** method |
| Custom control-point affine + parameters/residuals | `/coord_trans/` → **Custom control points** method |
| PROJ/pyproj CRS transform | `/crs/` → standard presets |
| NLIMS log-table Cassini | `/crs/` → `Cassini (log tables)` presets + central meridian |
| DMS / bearing formatting | `/bearing/`, `/traverse/`, `/area/` via shared `fayvadgeo/survey_math.py` |

CLI: `python -m georef.georef -i control_points.csv -v`

See `georef/README.md` for module reference. Research scripts are in `georef/research/`.

## Input file format (point uploads)

Plain text, one point per line: `x,y` (easting/northing or lon/lat per source CRS)

## Frontend

No Node.js or npm.

| Asset | Location |
|-------|----------|
| App styles | `static/site/css/app.css` |
| Map styles | `static/site/css/map.css` |
| Alpine.js | `static/site/js/alpine.min.js` |
| App scripts | `static/site/js/{app,crud,formset,map}.js` |

Optional local vendoring: `bash scripts/vendor-assets.sh`

## Docker (app in container, database on host)

PostgreSQL/PostGIS runs on the **host machine**. The web app runs in Docker and connects via `host.docker.internal`.

### 1. Prepare host database

```bash
sudo -u postgres psql -f docker/postgres-host-setup.sql
```

Edit `docker/postgres-host-setup.sql` with your password, then ensure Postgres accepts Docker connections (see comments in that file).

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env — URL-encode @ in passwords as %40
# DATABASE_URL=postgres://fayvad:your%40password@host.docker.internal:5432/fayvad_survey
```

### 3. Run

Gunicorn on port **8015**:

```bash
docker compose up --build
```

App URL: http://localhost:8015

Development (live code reload via gunicorn `--reload`):

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

Create a superuser inside the container:

```bash
docker compose exec web python manage.py createsuperuser
```

| Variable | Purpose |
|----------|---------|
| `WEB_PORT` | Host port (default `8015`) |
| `APP_PORT` | Gunicorn bind port inside the container (default `8015`) |

Static files are collected on container start and served via **WhiteNoise** (gunicorn does not serve `/static/` itself).

Settings module: `fayvadgeo.settings.docker`

## Local setup (without Docker)

1. Copy the sample environment file and edit it:

   ```bash
   cp fayvadgeo/settings/local.sample.env fayvadgeo/settings/local.env
   ```

2. Create a virtual environment and install dependencies:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. Create the database and run migrations:

   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

4. Start the development server:

   ```bash
   python manage.py runserver
   ```

## Deployment

Point DNS for **survey.fayvad.com** at your server and set:

```env
ALLOWED_HOSTS=survey.fayvad.com
CSRF_TRUSTED_ORIGINS=https://survey.fayvad.com
```
