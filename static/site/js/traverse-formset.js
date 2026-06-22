// Traverse leg formset — add rows without jQuery

(function () {
  'use strict';

  var MAX_FORMS = 20;

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
        alert('Maximum number of legs reached.');
        return;
      }
      var html = emptyTemplate.innerHTML.replace(/__prefix__/g, String(count));
      container.insertAdjacentHTML('beforeend', html);
      totalInput.value = String(count + 1);
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    initFormset(
      'traverse_form_set',
      'traverse_add_leg',
      'id_legs-TOTAL_FORMS',
      'traverse_empty_form'
    );
  });
})();
