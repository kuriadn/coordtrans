$(function () {

  /* Functions */

  var loadForm = function () {
    var btn = $(this);
    $.ajax({
      url: btn.attr("data-url"),
      type: 'get',
      dataType: 'json',
      beforeSend: function () {
        $("#modal-obj").modal("show");
      },
      success: function (data) {
        $("#modal-obj .modal-content").html(data.html_form);
      }
    });
  };

  var saveForm = function () {
    var form = $(this);
    $.ajax({
      url: form.attr("action"),
      data: form.serialize(),
      type: form.attr("method"),
      dataType: 'json',
      success: function (data) {
        if (data.form_is_valid) {
          $("#obj-table tbody").html(data.html_list);
          $("#modal-obj").modal("hide");
        }
        else {
          $("#modal-obj .modal-content").html(data.html_form);
        }
      }
    });
    return false;
  };


  /* Binding */

  // Create Object
  $(".js-create").click(loadForm);
  $("#modal-obj").on("submit", ".js-create-form", saveForm);

  // Update Object
  $("#obj-table").on("click", ".js-update", loadForm);
  $("#modal-obj").on("submit", ".js-update-form", saveForm);

  // Delete Object
  $("#obj-table").on("click", ".js-delete", loadForm);
  $("#modal-obj").on("submit", ".js-delete-form", saveForm);

});
