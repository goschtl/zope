

$(document).ready(
  function(){

    function hideTitle(){
      var title = $(this).attr("title");
      if (title){
        $(this).next('span').remove();
      }
    }

    function showTitle(){
      var title = $(this).attr("title");
      if (title){
        $(this)
          .after('<span>'+title+'</span>')
          .next('span').addClass('hint').hide().fadeIn('slow');
      }
    }

    $("input:text,textarea,select").focus(showTitle).blur(hideTitle);

    //set fields.
    $("select.select-widget.set-field").each(
      function(){
        var select = $(this);
        var selectId = select.attr('id');
        var selectedId = selectId + '-selected';
        var selectorId = selectId + '-selector';
        select.after('<div id="'+selectedId+'"></div>')
          .clone()
          .attr('multiple','')
          .attr('size','')
          .attr('id',selectorId)
          .attr('name','__ignore__')
          .prepend("<option value=\"--NOVALUE--\">Add</option>")
          .insertBefore(select);
        select.hide();

        var selector = $('#'+selectorId);
        var selected = $('#'+selectedId);

        function unfill(value){
          select.find('option[value="'+ value +'"]')
            .clone().insertAfter(selector.children()[0]);
          var values = select.val();
          delete values[$.inArray(value, values)];
          select.val(values);
          $(this).parent().remove();
          selector.val('--NOVALUE--');
        }

        function fill(){
          var option = $(this).find("option:selected");
          if (option.attr('value') === '--NOVALUE--'){
            return;
          }
          var contents = ""
            + "<div>"
            + "  <input type=\"button\" class=\"delete\""
            + "         value=\"X\"/>"
            + "  <span>"
            +      option.text()
            + "  </span>"
            + "</div>";
          selected.append(contents)
            .find('div:last input').click(function(){unfill.call(this, option.attr('value'));})
            .parent()
            .effect("highlight", {}, 1000);

          $(this).val('--NOVALUE--');

          select.val((select.val() || []).concat([option.attr('value')]));

          option.remove();
        }
        selector.change(fill);

        select.find('option:selected').each(
          function(){
            selector.val($(this).attr('value')).change();
          });

      });


    $("textarea.textarea-widget.list-field").each(
      function(){
        var textarea = $(this);
        textarea.hide();
        var textareaId = textarea.attr('id');
        var wrapperId = textareaId + '-wrapper';
        textarea.before("<div id=\""+wrapperId+"\"></div>");
        var wrapper = $("#"+wrapperId);

        wrapper
          .append("<input type=\"text\" />")
          .append("<input type=\"button\" value=\"Add\"/> ")
          .append("<div class=\"list-field-added\"></div>");

        var addButton = wrapper.find(":button");
        var input = wrapper.find(":text");
        var added = wrapper.find("div");

        function strip(s){
          return s.replace(/^\W*/g,"")
                  .replace(/\W*$/g,"");
        }

        function updateTextArea(){
          textarea.val("");
          added.find("span").each(
            function(){
              textarea.val(textarea.val()+strip($(this).html())+'\n');
            });
        }

        function addValue(val){
          var contents = ""
            + "<div class=\"list-field-added-row\">"
            + "  <input type=\"button\" class=\"delete\""
            + "         value=\"X\"/>"
            + "  <span>"
            +      val
            + "  </span>"
            + "</div>";
          added.append(contents)
            .find("div:last input")
            .click(
              function(){
                $(this).parent().remove();
                updateTextArea();
              })
            .parent()
            .effect("highlight", {}, 1000);
        }

        addButton.click(
          function(){
            addValue(input.val());
            input.val("");
            updateTextArea();
          });

        input.keypress(
          function(e){
            if (e.which == 13){
              addButton.click();
              e.preventDefault();
            }
          });

        input.focus(function(){textarea.triggerHandler("focus");});
        input.blur(function(){textarea.triggerHandler("blur");});

        added.hide();
        var lines = strip(textarea.val()).split('\n');
        for (var i=0; i<lines.length; i++){
          var val = strip(lines[i]);
          if (val){
            addValue(val);
            updateTextArea();
          }
        }
        added.show();

      });

  });