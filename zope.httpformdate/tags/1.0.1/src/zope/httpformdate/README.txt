
Tests of zope.httpformdate
==========================

Register the ``:date`` converter.

    >>> from zope.httpformdate import register
    >>> register()

Use it in a form.

    >>> from pprint import pprint
    >>> from zope.httpform import parse
    >>> env = {'REQUEST_METHOD': 'GET', 'QUERY_STRING': 'x:date=2009-02-28'}
    >>> pprint(parse(env))
    {u'x': datetime.datetime(2009, 2, 28, 0, 0)}

The parser supports English month and weekday names.

    >>> env['QUERY_STRING'] = 'x:date=February+7,+2009'
    >>> pprint(parse(env))
    {u'x': datetime.datetime(2009, 2, 7, 0, 0)}

The parser supports times.

    >>> env['QUERY_STRING'] = 'x:date=February+7,+2009+4:30PM'
    >>> pprint(parse(env))
    {u'x': datetime.datetime(2009, 2, 7, 16, 30)}

