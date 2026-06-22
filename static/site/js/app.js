// FayvadGeo — global UI helpers (vanilla JS)

document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('[data-dismiss="alert"]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var alert = btn.closest('.alert');
      if (alert) {
        alert.remove();
      }
    });
  });
});
