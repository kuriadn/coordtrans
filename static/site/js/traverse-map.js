/**
 * Traverse plan / map view — Leaflet with leg labels (bearing + distance).
 */
(function () {
  'use strict';

  function stationIcon(name, isStart) {
    var color = isStart ? '#7c3aed' : '#059669';
    return L.divIcon({
      className: 'traverse-station-icon',
      html:
        '<span class="traverse-station-marker" style="background:' + color + '"></span>' +
        '<span class="traverse-station-name">' + name + '</span>',
      iconSize: [0, 0],
      iconAnchor: [7, 7],
    });
  }

  function mapCoords(st, planMode) {
    if (planMode) {
      return [st.n, st.e];
    }
    return [st.lat, st.lng];
  }

  function legAngle(from, to, planMode) {
    if (planMode) {
      return (Math.atan2(to.e - from.e, to.n - from.n) * 180) / Math.PI;
    }
    return (Math.atan2(to.lng - from.lng, to.lat - from.lat) * 180) / Math.PI;
  }

  function legLabelHtml(leg, angle) {
    return (
      '<div class="traverse-leg-label-inner" style="transform:rotate(' + angle + 'deg)">' +
      '<span class="traverse-leg-dist">' + leg.distance_label + '</span>' +
      '<span class="traverse-leg-bearing">' + leg.bearing_label + '</span>' +
      '</div>'
    );
  }

  window.FayvadTraverseMap = {
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

      var groups = {
        traverse: L.layerGroup().addTo(map),
        stations: L.layerGroup().addTo(map),
        labels: L.layerGroup().addTo(map),
      };

      function extendBounds(latlng) {
        if (latlng[0] == null || latlng[1] == null) {
          return;
        }
        bounds.push(latlng);
      }

      (payload.legs || []).forEach(function (leg) {
        var from = leg.from;
        var to = leg.to;
        var a = mapCoords(from, planMode);
        var b = mapCoords(to, planMode);
        extendBounds(a);
        extendBounds(b);

        var line = L.polyline([a, b], {
          color: '#047857',
          weight: 3,
          opacity: 0.9,
        });
        line.bindPopup(
          '<strong>' + leg.from_station + ' → ' + leg.to_station + '</strong><br>' +
          'Distance: ' + leg.distance_label + '<br>' +
          'Bearing: ' + leg.bearing_label
        );
        groups.traverse.addLayer(line);

        var mid = [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2];
        var angle = legAngle(from, to, planMode);
        if (angle > 90 || angle < -90) {
          angle += 180;
        }

        var label = L.marker(mid, {
          icon: L.divIcon({
            className: 'traverse-leg-label',
            html: legLabelHtml(leg, angle),
            iconSize: [0, 0],
          }),
          interactive: false,
          zIndexOffset: 400,
        });
        groups.labels.addLayer(label);
      });

      (payload.stations || []).forEach(function (st, idx) {
        var latlng = mapCoords(st, planMode);
        extendBounds(latlng);
        var marker = L.marker(latlng, {
          icon: stationIcon(st.name, idx === 0),
          zIndexOffset: 500,
        });
        marker.bindPopup(
          '<strong>' + st.name + '</strong><br>' +
          'E: ' + Number(st.e).toFixed(3) + '<br>' +
          'N: ' + Number(st.n).toFixed(3)
        );
        groups.stations.addLayer(marker);
      });

      var center = payload.default_center || [-1.286389, 36.817223];
      if (bounds.length) {
        map.fitBounds(bounds, { padding: [48, 48], maxZoom: planMode ? 4 : 18 });
      } else if (!planMode) {
        map.setView(center, payload.default_zoom || 12);
      }

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
        } else {
          layers.osm.addTo(map);
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
          if (bounds.length) {
            map.fitBounds(bounds, { padding: [48, 48], maxZoom: planMode ? 4 : 18 });
          }
        },
        resetView: function () {
          if (bounds.length) {
            map.fitBounds(bounds, { padding: [48, 48], maxZoom: planMode ? 4 : 18 });
          } else if (!planMode) {
            map.setView(center, payload.default_zoom || 12);
          }
        },
        toggleLayer: function (name, visible) {
          if (visible) {
            map.addLayer(groups[name]);
          } else {
            map.removeLayer(groups[name]);
          }
        },
      };
    },
  };

  document.addEventListener('DOMContentLoaded', function () {
    var el = document.getElementById('traverse-map-data');
    if (!el) {
      return;
    }

    var payload = JSON.parse(el.textContent);
    var googleKey = el.getAttribute('data-google-key') || '';
    var api = window.FayvadTraverseMap.init('traverse-map', payload, googleKey);
    if (!api) {
      return;
    }
    window.fayvadTraverseMapApi = api;

    document.querySelectorAll('input[name="traverse-basemap"]').forEach(function (radio) {
      radio.addEventListener('change', function () {
        if (radio.checked) {
          api.setBasemap(radio.value);
        }
      });
    });

    var bind = function (id, fn) {
      var btn = document.getElementById(id);
      if (btn) {
        btn.addEventListener('click', fn);
      }
    };

    bind('traverse-map-zoom-in', function () { api.zoomIn(); });
    bind('traverse-map-zoom-out', function () { api.zoomOut(); });
    bind('traverse-map-fit', function () { api.fitData(); });
    bind('traverse-map-reset', function () { api.resetView(); });

    ['traverse', 'stations', 'labels'].forEach(function (layer) {
      var checkbox = document.getElementById('traverse-layer-' + layer);
      if (checkbox) {
        checkbox.addEventListener('change', function () {
          api.toggleLayer(layer, checkbox.checked);
        });
      }
    });
  });
})();
