// Django formset — add rows without jQuery

(function () {
  'use strict';

  var MAX_FORMS = 13;

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
        alert(
          'The maximum number of direct entries has been reached. ' +
          'Prepare additional points as a file and upload instead.'
        );
        return;
      }
      var html = emptyTemplate.innerHTML.replace(/__prefix__/g, String(count));
      container.insertAdjacentHTML('beforeend', html);
      totalInput.value = String(count + 1);
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    initFormset('form_set', 'add_point', 'id_form-TOTAL_FORMS', 'empty_form');
  });
})();
