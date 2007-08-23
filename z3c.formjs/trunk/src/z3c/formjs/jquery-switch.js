function switchWidget(widgetId, mode, code) {
    element = $('#' + widgetId + '-row div.widget');
    element.html(code);
    if (mode == 'input') {
        $('#' + widgetId).focus()
    }
}

function saveWidget(widgetId, msg) {
    element = $('#' + widgetId + '-row div.error');
    if (element) {
        element.remove();
    }
    $('#' + widgetId + '-row').append(
        '<div class="error">' + msg+  '</div>');

    var error = false;
    if (msg != '') {
        $('#' + widgetId).removeClass('valid');
        $('#' + widgetId).addClass('invalid');
        $('#' + widgetId).focus()
        error = true;
    }
    else {
        $('#' + widgetId).removeClass('invalid');
        $('#' + widgetId).addClass('valid');
    }
    return error
}
