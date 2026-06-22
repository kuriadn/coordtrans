/**
 * FayvadGeo transformation map — Leaflet + vanilla JS (no Node build).
 */
(function () {
  'use strict';

  function icon(color) {
    return L.divIcon({
      className: '',
      html: '<span style="background:' + color + ';width:14px;height:14px;border:2px solid #fff;border-radius:50%;box-shadow:0 0 0 1px rgba(15,23,42,.25);display:block;"></span>',
      iconSize: [14, 14],
      iconAnchor: [7, 7],
    });
  }

  function popupHtml(title, e, n, system, extra) {
    return (
      '<strong>' + title + '</strong><br>' +
      'E: ' + Number(e).toFixed(3) + '<br>' +
      'N: ' + Number(n).toFixed(3) + '<br>' +
      '<span style="color:#64748b">' + system + '</span>' +
      (extra ? '<br>' + extra : '')
    );
  }

  window.FayvadGeoMap = {
    init: function (containerId, payload, googleApiKey) {
      if (!window.L || !payload) {
        return null;
      }

      var map = L.map(containerId, {
        zoomControl: false,
        attributionControl: true,
      });

      var layers = {
        osm: L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
          maxZoom: 19,
          attribution: '&copy; OpenStreetMap contributors',
        }),
        esriStreet: L.tileLayer(
          'https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}',
          { maxZoom: 19, attribution: 'Tiles &copy; Esri' }
        ),
        esriImagery: L.tileLayer(
          'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
          { maxZoom: 19, attribution: 'Tiles &copy; Esri' }
        ),
      };

      var googleLayer = null;
      if (googleApiKey && L.gridLayer && L.gridLayer.googleMutant) {
        googleLayer = L.gridLayer.googleMutant({ type: 'roadmap', maxZoom: 21 });
        layers.google = googleLayer;
      }

      layers.osm.addTo(map);

      var groups = {
        input: L.layerGroup().addTo(map),
        output: L.layerGroup().addTo(map),
        control: L.layerGroup().addTo(map),
        links: L.layerGroup().addTo(map),
      };

      var bounds = [];

      function addPoint(lat, lng, layer, markerIcon, popup) {
        if (lat == null || lng == null) {
          return;
        }
        var marker = L.marker([lat, lng], { icon: markerIcon });
        if (popup) {
          marker.bindPopup(popup);
        }
        layer.addLayer(marker);
        bounds.push([lat, lng]);
      }

      (payload.points || []).forEach(function (pt) {
        var inp = pt.input || {};
        var out = pt.output || {};
        addPoint(
          inp.lat,
          inp.lng,
          groups.input,
          icon('#2563eb'),
          popupHtml('Input #' + pt.id, inp.e, inp.n, inp.system)
        );
        if (pt.status === 'ok' && out.lat != null) {
          addPoint(
            out.lat,
            out.lng,
            groups.output,
            icon('#059669'),
            popupHtml('Transformed #' + pt.id, out.e, out.n, out.system)
          );
          if (inp.lat != null && out.lat != null) {
            groups.links.addLayer(
              L.polyline(
                [[inp.lat, inp.lng], [out.lat, out.lng]],
                { color: '#64748b', weight: 1.5, dashArray: '4 4' }
              )
            );
          }
        }
      });

      (payload.controls || []).forEach(function (cp) {
        addPoint(
          cp.lat,
          cp.lng,
          groups.control,
          icon('#7c3aed'),
          popupHtml(cp.label, cp.e, cp.n, 'Control')
        );
      });

      var center = payload.default_center || [-1.286389, 36.817223];
      if (bounds.length) {
        map.fitBounds(bounds, { padding: [40, 40], maxZoom: 16 });
      } else {
        map.setView(center, payload.default_zoom || 12);
      }

      function setBasemap(name) {
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
            map.fitBounds(bounds, { padding: [40, 40], maxZoom: 16 });
          }
        },
        resetView: function () {
          map.setView(center, payload.default_zoom || 12);
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
    var el = document.getElementById('transform-map-data');
    if (!el) {
      return;
    }

    var payload = JSON.parse(el.textContent);
    var googleKey = el.getAttribute('data-google-key') || '';
    var api = window.FayvadGeoMap.init('transform-map', payload, googleKey);
    if (!api) {
      return;
    }
    window.fayvadGeoMapApi = api;

    document.querySelectorAll('input[name="basemap"]').forEach(function (radio) {
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

    bind('map-zoom-in', function () { api.zoomIn(); });
    bind('map-zoom-out', function () { api.zoomOut(); });
    bind('map-fit', function () { api.fitData(); });
    bind('map-reset', function () { api.resetView(); });

    ['input', 'output', 'control', 'links'].forEach(function (layer) {
      var checkbox = document.getElementById('layer-' + layer);
      if (checkbox) {
        checkbox.addEventListener('change', function () {
          api.toggleLayer(layer, checkbox.checked);
        });
      }
    });
  });
})();
