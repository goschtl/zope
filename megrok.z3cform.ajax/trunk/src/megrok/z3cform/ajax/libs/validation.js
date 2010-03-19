$(document).ready(function() {
    var form = $('form');
    $('input').blur(function(){
        value = $(this).val()
        console.log('hhhh', value);
      $.ajax({
          type: "POST",
          url: form.attr('action') + '/++validate++field',
          data: value,
          dataType: "json",
          async: false,
          success: function(data) {
              if (data.success == true) {
                  success = true;
              }
              else {
                  success = false;
                  errors = data.errors
              }
          }
      });

    })
});


