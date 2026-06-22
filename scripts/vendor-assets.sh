#!/usr/bin/env bash
# Re-vendor frontend assets (no Node.js required).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LEAFLET="$ROOT/static/site/vendor/leaflet"
mkdir -p "$LEAFLET/images"

curl -fsSL -o "$ROOT/static/site/js/alpine.min.js" \
  https://cdn.jsdelivr.net/npm/alpinejs@3.14.9/dist/cdn.min.js

curl -fsSL -o "$LEAFLET/leaflet.css" https://unpkg.com/leaflet@1.9.4/dist/leaflet.css
curl -fsSL -o "$LEAFLET/leaflet.js" https://unpkg.com/leaflet@1.9.4/dist/leaflet.js
curl -fsSL -o "$LEAFLET/images/marker-icon.png" https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png
curl -fsSL -o "$LEAFLET/images/marker-icon-2x.png" https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png
curl -fsSL -o "$LEAFLET/images/marker-shadow.png" https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png
curl -fsSL -o "$LEAFLET/leaflet.gridlayer.googlemutant.js" \
  https://unpkg.com/leaflet.gridlayer.googlemutant@0.15.0/dist/Leaflet.GoogleMutant.js

echo "Vendored alpine.min.js and Leaflet 1.9.4 under static/site/"
