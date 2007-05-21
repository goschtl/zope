$(document).ready(function() {
    $('#dock').Fisheye(
        {maxWidth: 60,
         items: 'a',
         itemsText: 'span',
         container: '.dock-container',
         itemWidth: 53,
         proximity: 90,
         halign : 'center'}
    );
    $('input').jqJSONValidate();
    $('textarea').jqJSONValidate();
});
