// Boundary point formset

(function () {
  'use strict';

  var MAX_FORMS = 30;

  function initFormset(containerId, addBtnId, totalFormsId, emptyTemplateId) {
    var container = document.getElementById(containerId);
    var addBtn = document.getElementById(addBtnId);
    var totalInput = document.getElementById(totalFormsId);
    var emptyTemplate = document.getElementById(emptyTemplateId);

    if (!container || !addBtn || !totalInput || !emptyTemplate) {
      return;
    }

    addBtn.addEventListener('click', function () {
      var count = parseInt(totalInput.value, 10);
      if (count >= MAX_FORMS) {
        alert('Maximum number of points reached.');
        return;
      }
      var html = emptyTemplate.innerHTML.replace(/__prefix__/g, String(count));
      container.insertAdjacentHTML('beforeend', html);
      totalInput.value = String(count + 1);
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    initFormset('area_form_set', 'area_add_point', 'id_pts-TOTAL_FORMS', 'area_empty_form');
  });
})();
