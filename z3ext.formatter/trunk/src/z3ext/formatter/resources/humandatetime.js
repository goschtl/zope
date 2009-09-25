var my_dictionary = {
    'year(s) ago'  : 'year(s) ago',
    'month(s) ago'  : 'month(s) ago',
    'weeks(s) ago': 'weeks(s) ago',
    'days(s) ago' : 'days(s) ago',
    'hours(s) ago' : 'hours(s) ago',
    'minutes(s) ago' : 'minutes(s) ago',
    'second(s) ago' : 'second(s) ago'
};

$.i18n.setDictionary(my_dictionary);

function setFormatter(el)
{
    var time = new Date()
    time.setTime(Date.parse(el.attr('value')));
    var new_time = new Date();
    delta = new_time-time;
    years = Math.floor(delta/(365*24*60*60*1000.0));
    months = Math.floor(delta/(30*24*60*60*1000.0));
    weeks = Math.floor(delta/(7*24*60*60*1000.0));
    days = Math.floor(delta/(24*60*60*1000.0));
    hours = Math.floor(delta/(60*60*1000.0));
    minutes = Math.floor(delta/(60*1000.0));
    seconds = Math.floor(delta/(1000.0));
    var res;
    if (years)
        res = years + ' ' +$.i18n._('year(s) ago')
    else if (months)
        res = months + ' ' +$.i18n._('month(s) ago')
    else if (weeks)
        res = weeks + ' ' +$.i18n._('weeks(s) ago')
    else if (days)
        res = days + ' ' +$.i18n._('days(s) ago')
    else if (hours)
        res = hours + ' ' +$.i18n._('hours(s) ago')
    else if (minutes)
        res = minutes + ' ' +$.i18n._('minutes(s) ago')
    else
        res = seconds + ' ' +$.i18n._('second(s) ago')
    el.text(res);
    el.attr('processed', 'true')
}


$(document).ready(function() {
    var elems = $("span.z3ext-formatter-humandatetime");
    for (var i = 0; i < elems.length; i++)
    {
        var el = $(elems[i]);
        if (!el.attr('processed')) {
            setFormatter(el);
        }
    }
});

/*
d1 = datetime.now(utc)
d2 = value.astimezone(utc)

delta = d1 - d2

years, months, weeks, hours, minutes = (
    delta.days/365, delta.days/30, delta.days/7,
    delta.seconds/3600, delta.seconds/60)

if years > 0:
    return translate(
        u'${value} year(s) ago', 'z3ext.formatter',
        mapping={'value': years})

if months > 0:
    return translate(u'${value} month(s) ago', 'z3ext.formatter',
                     mapping={'value': months})

if weeks > 0:
    return translate(u'${value} week(s) ago', 'z3ext.formatter',
                     mapping={'value': weeks})

if delta.days > 0:
    return translate(u'${value} day(s) ago', 'z3ext.formatter',
                     mapping={'value': delta.days})

if hours > 0:
    return translate(u'${value} hour(s) ago', 'z3ext.formatter',
                     mapping={'value': hours})

if minutes > 0:
    return translate(u'${value} minute(s) ago', 'z3ext.formatter',
                     mapping={'value': minutes})

return translate(u'${value} second(s) ago', 'z3ext.formatter',
                 mapping={'value': delta.seconds})
*/