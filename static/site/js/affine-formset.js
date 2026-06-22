(function () {
  var addBtn = document.getElementById('add_control');
  var container = document.getElementById('ctrl_form_set');
  var tmpl = document.getElementById('empty_ctrl_form');
  var totalInput = document.querySelector('#id_ctrl-TOTAL_FORMS');
  if (!addBtn || !container || !tmpl || !totalInput) return;

  addBtn.addEventListener('click', function () {
    var index = parseInt(totalInput.value, 10);
    var html = tmpl.innerHTML.replace(/__prefix__/g, index);
    var wrapper = document.createElement('div');
    wrapper.innerHTML = html;
    container.appendChild(wrapper.firstElementChild);
    totalInput.value = index + 1;
  });
})();
