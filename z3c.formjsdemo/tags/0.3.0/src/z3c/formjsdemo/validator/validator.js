function applyErrorMessage(widgetId, msg) {
    element = $('#' + widgetId + '-row div.error');
    if (element) {
        element.remove();
    }
    $('#' + widgetId + '-row').append(
        '<div class="error">' + msg+  '</div>');

    if (msg != '') {
        $('#' + widgetId).removeClass('valid');
        $('#' + widgetId).addClass('invalid');
    }
    else {
        $('#' + widgetId).removeClass('invalid');
        $('#' + widgetId).addClass('valid');
    }
}
