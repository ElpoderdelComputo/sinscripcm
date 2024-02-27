// Espera a que el documento esté completamente cargado antes de ejecutar cualquier código
$(document).ready(function() {
  var form = $('#formulario');

  form.on('submit', function(event) {
    event.preventDefault();

    var username = $('#username').val();
    var password = $('#password').val();

    $.ajax({
      type: 'POST',
      url: $(this).attr('action'),
      data: {
        'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val(),
        'username': username,
        'password': password
      },
      headers: {
        'X-CSRFToken': $('input[name=csrfmiddlewaretoken]').val()
      },
      success: function(response) {
        window.location.href = '/mostrar_cursos/';
      },
      error: function(xhr, status, error) {
        var response = JSON.parse(xhr.responseText);
        if (response.hasOwnProperty('error_message')) {
          $('#error-message').text(response.error_message);
        } else {
          $('#error-message').text('Ha ocurrido un error en la autenticación.');
        }
      }
    });
  });
});

