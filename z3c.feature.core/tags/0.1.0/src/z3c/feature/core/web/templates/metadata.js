$(document).ready(
  function(){

    $("label[for='form-widgets-license'] span").html("Custom License");

    if ($(this).find("option:selected").val() !== '--NOVALUE--'){
      $("#form-widgets-license-row").hide();
    }

    $("#form-widgets-commonLicense-novalue")
      .html("Choose my own license")
      .parent()
      .change(
        function(){
          var selected = $(this).find("option:selected").val();
          $("#form-widgets-license").val("");
          if (selected == '--NOVALUE--'){
            $("#form-widgets-license-row").show();
            $("#form-widgets-license").focus();
          } else {
            $("#form-widgets-license-row").hide();
          }
        });

  });
