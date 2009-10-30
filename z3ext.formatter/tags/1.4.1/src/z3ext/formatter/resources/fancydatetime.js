function setFancydatetimeFormatter(el)
{
    var time = new Date();
    var value = el.attr('value');
    time.setTime(Date.parse(value));
    var new_time = new Date();
    delta = new_time-time;
    if (delta < 0) {
        delta = Math.abs(delta);
    }
    years = Math.floor(delta/(365*24*60*60*1000.0));
    months = Math.floor(delta/(30*24*60*60*1000.0));
    weeks = Math.floor(delta/(7*24*60*60*1000.0));
    days = Math.floor(delta/(24*60*60*1000.0));
    hours = Math.floor(delta/(60*60*1000.0));
    minutes = Math.floor(delta/(60*1000.0));

    var res;

    if (!years && !months && !weeks && days == 1) {
        res = 'Yesterday at ' + el.attr('time');

    } else if (!years & !months & !weeks & days == 0) {
        res = 'Today at ' + el.attr('time');
    } else {
        res = el.attr('date') + ' ' + el.attr('time');
    }

    el.text(res);
    el.attr('processed', 'true')
}


$(document).ready(function() {
    
    var elems = $("span.z3ext-formatter-fancydatetime");
    for (var i = 0; i < elems.length; i++)
    {
        var el = $(elems[i]);
        if (!el.attr('processed')) {
            setFancydatetimeFormatter(el);
        }
    }
});
