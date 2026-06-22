/**
 * Bearing / distance map — single leg with labels.
 */
(function () {
  'use strict';

  function stationIcon(label, isFrom) {
    var color = isFrom ? '#7c3aed' : '#059669';
    return L.divIcon({
      className: 'traverse-station-icon',
      html:
        '<span class="traverse-station-marker" style="background:' + color + '"></span>' +
        '<span class="traverse-station-name">' + label + '</span>',
      iconSize: [0, 0],
      iconAnchor: [7, 7],
    });
  }

  function mapCoords(pt, planMode) {
    if (planMode) {
      return [pt.n, pt.e];
    }
    return [pt.lat, pt.lng];
  }

  window.FayvadGeocalcMap = {
    init: function (containerId, payload, googleApiKey) {
      if (!window.L || !payload) {
        return null;
      }

      var planMode = payload.mode === 'plan';
      var mapOptions = { zoomControl: false, attributionControl: !planMode };
      if (planMode) {
        mapOptions.crs = L.CRS.Simple;
      }

      var map = L.map(containerId, mapOptions);
      var layers = {};
      var bounds = [];

      if (!planMode) {
        layers.osm = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
          maxZoom: 19,
          attribution: '&copy; OpenStreetMap contributors',
        });
        layers.esriStreet = L.tileLayer(
          'https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}',
          { maxZoom: 19, attribution: 'Tiles &copy; Esri' }
        );
        layers.esriImagery = L.tileLayer(
          'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
          { maxZoom: 19, attribution: 'Tiles &copy; Esri' }
        );
        if (googleApiKey && L.gridLayer && L.gridLayer.googleMutant) {
          layers.google = L.gridLayer.googleMutant({ type: 'roadmap', maxZoom: 21 });
        }
        layers.osm.addTo(map);
      }

      var from = payload.from;
      var to = payload.to;
      var edge = payload.edge;
      var a = mapCoords(from, planMode);
      var b = mapCoords(to, planMode);
      bounds.push(a, b);

      L.polyline([a, b], { color: '#047857', weight: 3, opacity: 0.95 }).addTo(map);

      var mid = [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2];
      var angle = planMode
        ? Math.atan2(to.e - from.e, to.n - from.n) * 180 / Math.PI
        : Math.atan2(to.lng - from.lng, to.lat - from.lat) * 180 / Math.PI;
      if (angle > 90 || angle < -90) {
        angle += 180;
      }

      L.marker(mid, {
        icon: L.divIcon({
          className: 'traverse-leg-label',
          html:
            '<div class="traverse-leg-label-inner" style="transform:rotate(' + angle + 'deg)">' +
            '<span class="traverse-leg-dist">' + edge.distance_label + '</span>' +
            '<span class="traverse-leg-bearing">' + edge.bearing_label + '</span>' +
            '</div>',
          iconSize: [0, 0],
        }),
        interactive: false,
      }).addTo(map);

      L.marker(a, { icon: stationIcon(from.label, true), zIndexOffset: 500 })
        .bindPopup('<strong>' + from.label + '</strong><br>E ' + from.e + '<br>N ' + from.n)
        .addTo(map);
      L.marker(b, { icon: stationIcon(to.label, false), zIndexOffset: 500 })
        .bindPopup('<strong>' + to.label + '</strong><br>E ' + to.e + '<br>N ' + to.n)
        .addTo(map);

      var center = payload.default_center || [-1.286389, 36.817223];
      map.fitBounds(bounds, { padding: [56, 56], maxZoom: planMode ? 4 : 18 });

      function setBasemap(name) {
        if (planMode) {
          return;
        }
        Object.keys(layers).forEach(function (key) {
          if (map.hasLayer(layers[key])) {
            map.removeLayer(layers[key]);
          }
        });
        if (layers[name]) {
          layers[name].addTo(map);
        }
      }

      return {
        map: map,
        setBasemap: setBasemap,
        invalidate: function () {
          setTimeout(function () { map.invalidateSize(); }, 50);
        },
        zoomIn: function () { map.zoomIn(); },
        zoomOut: function () { map.zoomOut(); },
        fitData: function () {
          map.fitBounds(bounds, { padding: [56, 56], maxZoom: planMode ? 4 : 18 });
        },
        resetView: function () {
          map.fitBounds(bounds, { padding: [56, 56], maxZoom: planMode ? 4 : 18 });
        },
      };
    },
  };

  document.addEventListener('DOMContentLoaded', function () {
    var el = document.getElementById('geocalc-map-data');
    if (!el) {
      return;
    }
    var api = window.FayvadGeocalcMap.init(
      'geocalc-map',
      JSON.parse(el.textContent),
      el.getAttribute('data-google-key') || ''
    );
    if (!api) {
      return;
    }
    window.fayvadGeocalcMapApi = api;

    document.querySelectorAll('input[name="geocalc-basemap"]').forEach(function (radio) {
      radio.addEventListener('change', function () {
        if (radio.checked) {
          api.setBasemap(radio.value);
        }
      });
    });

    ['geocalc-map-zoom-in', 'geocalc-map-zoom-out', 'geocalc-map-fit', 'geocalc-map-reset'].forEach(function (id, i) {
      var btn = document.getElementById(id);
      if (btn) {
        btn.addEventListener('click', [api.zoomIn, api.zoomOut, api.fitData, api.resetView][i]);
      }
    });
  });
})();
