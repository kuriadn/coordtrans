// CRUD modal AJAX — replaces jQuery script.js

(function () {
  'use strict';

  function getCookie(name) {
    var match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
    return match ? decodeURIComponent(match[2]) : null;
  }

  function openModal(html) {
    var backdrop = document.getElementById('modal-obj');
    if (!backdrop) return;
    var content = backdrop.querySelector('.modal-panel');
    if (content) {
      content.innerHTML = html;
    }
    backdrop.classList.add('open');
    backdrop.setAttribute('aria-hidden', 'false');
  }

  function closeModal() {
    var backdrop = document.getElementById('modal-obj');
    if (!backdrop) return;
    backdrop.classList.remove('open');
    backdrop.setAttribute('aria-hidden', 'true');
    var content = backdrop.querySelector('.modal-panel');
    if (content) {
      content.innerHTML = '';
    }
  }

  function loadForm(url) {
    fetch(url, {
      headers: { 'X-Requested-With': 'XMLHttpRequest' },
    })
      .then(function (res) { return res.json(); })
      .then(function (data) {
        openModal(data.html_form);
      });
  }

  function saveForm(form) {
    var body = new FormData(form);
    fetch(form.action, {
      method: form.method || 'POST',
      body: body,
      headers: { 'X-Requested-With': 'XMLHttpRequest' },
    })
      .then(function (res) { return res.json(); })
      .then(function (data) {
        if (data.form_is_valid) {
          var tbody = document.querySelector('#obj-table tbody');
          if (tbody) {
            tbody.innerHTML = data.html_list;
          }
          closeModal();
        } else {
          openModal(data.html_form);
        }
      });
    return false;
  }

  document.addEventListener('click', function (e) {
    var createBtn = e.target.closest('.js-create');
    if (createBtn) {
      e.preventDefault();
      loadForm(createBtn.getAttribute('data-url'));
      return;
    }

    var updateBtn = e.target.closest('.js-update');
    if (updateBtn) {
      e.preventDefault();
      loadForm(updateBtn.getAttribute('data-url'));
      return;
    }

    var deleteBtn = e.target.closest('.js-delete');
    if (deleteBtn) {
      e.preventDefault();
      loadForm(deleteBtn.getAttribute('data-url'));
      return;
    }

    if (e.target.closest('[data-modal-close]')) {
      e.preventDefault();
      closeModal();
    }

    var backdrop = document.getElementById('modal-obj');
    if (backdrop && e.target === backdrop) {
      closeModal();
    }
  });

  document.addEventListener('submit', function (e) {
    var form = e.target;
    if (form.matches('.js-create-form, .js-update-form, .js-delete-form')) {
      e.preventDefault();
      saveForm(form);
    }
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      closeModal();
    }
  });
})();
