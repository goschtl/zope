
Tests of zope.httpform
======================

Basic Usage
-----------

The FormParser class expects a subset of a WSGI environment.  Start with
a simple form.

    >>> import pprint
    >>> from zope.httpform import FormParser
    >>> env = {'REQUEST_METHOD': 'GET', 'QUERY_STRING': 'x=1&y=my+data&z='}
    >>> pprint.pprint(FormParser(env).parse())
    {u'x': u'1', u'y': u'my data', u'z': u''}

Now let's start using some of the features of this package.  Use the `:int`
suffix on the variable name:

    >>> env['QUERY_STRING'] = 'x:int=1&y:int=2'
    >>> pprint.pprint(FormParser(env).parse())
    {u'x': 1, u'y': 2}

Floating point and long integers work too:

    >>> env['QUERY_STRING'] = 'x:float=1&y:float=2&z:long=3&zz:long=4L'
    >>> pprint.pprint(FormParser(env).parse())
    {u'x': 1.0, u'y': 2.0, u'z': 3L, u'zz': 4L}

The `:boolean` suffix is good for HTML checkboxes:

    >>> env['QUERY_STRING'] = 'x:boolean=checked&y:boolean='
    >>> pprint.pprint(FormParser(env).parse())
    {u'x': True, u'y': False}

Lists and Tuples
----------------

What happens if variables get repeated?

    >>> env['QUERY_STRING'] = 'x=0&x=a&x=b&x:int=1&x:float=2'
    >>> pprint.pprint(FormParser(env).parse())
    {u'x': [u'0', u'a', u'b', 1, 2.0]}

That's reasonable, but it's even better to use the `:list` suffix so that
field values are a list even when they occur only once.

    >>> env['QUERY_STRING'] = 'x:int:list=1'
    >>> pprint.pprint(FormParser(env).parse())
    {u'x': [1]}

Another variation:

    >>> env['QUERY_STRING'] = 'x:list:int=1'
    >>> pprint.pprint(FormParser(env).parse())
    {u'x': [1]}

Empty values are preserved:

    >>> env['QUERY_STRING'] = 'x:list=a&x:list='
    >>> pprint.pprint(FormParser(env).parse())
    {u'x': [u'a', u'']}

Order is preserved:

    >>> env['QUERY_STRING'] = 'x:list=c&x:list=b&x:list=a'
    >>> pprint.pprint(FormParser(env).parse())
    {u'x': [u'c', u'b', u'a']}

Empty values are not preserved if you use the ignore_empty suffix:

    >>> env['QUERY_STRING'] = 'x:list:ignore_empty=a&x:list:ignore_empty='
    >>> pprint.pprint(FormParser(env).parse())
    {u'x': [u'a']}

Use `:tuple` to generate a tuple instead of a list.  Note that the order
of the field values is always preserved.

    >>> env['QUERY_STRING'] = 'x:int:tuple=2&x:int:tuple=1'
    >>> pprint.pprint(FormParser(env).parse())
    {u'x': (2, 1)}

A value can become a list:

    >>> env['QUERY_STRING'] = 'x:int=0&x:int:list=1'
    >>> pprint.pprint(FormParser(env).parse())
    {u'x': [0, 1]}

Default Values
--------------

Sometimes it's useful for a form to provide a default value.

    >>> env['QUERY_STRING'] = 'country:default=United+States'
    >>> pprint.pprint(FormParser(env).parse())
    {u'country': u'United States'}
    >>> env['QUERY_STRING'] = 'country:default=United+States&country=Ireland'
    >>> pprint.pprint(FormParser(env).parse())
    {u'country': u'Ireland'}

An empty value overrides a default value, unless the potentially
empty value uses the `:ignore_empty` suffix.

    >>> env['QUERY_STRING'] = 'country:default=US&country='
    >>> pprint.pprint(FormParser(env).parse())
    {u'country': u''}
    >>> env['QUERY_STRING'] = 'country:default=US&country:ignore_empty='
    >>> pprint.pprint(FormParser(env).parse())
    {u'country': u'US'}

A default value takes the place of an empty value.

    >>> env['QUERY_STRING'] = 'x:int:default=0&x:int='
    >>> pprint.pprint(FormParser(env).parse())
    {u'x': 0}

A default list value will be added to the list unless it has already
been added.

    >>> env['QUERY_STRING'] = 'x:list:default=always'
    >>> pprint.pprint(FormParser(env).parse())
    {u'x': [u'always']}
    >>> env['QUERY_STRING'] = 'x:list:default=always&x:list=always'
    >>> pprint.pprint(FormParser(env).parse())
    {u'x': [u'always']}
    >>> env['QUERY_STRING'] = 'x:list:default=always&x:list=never'
    >>> pprint.pprint(FormParser(env).parse())
    {u'x': [u'never', u'always']}

Required Values
---------------

The `:required` suffix raises `ValueError` if the field is left empty.

    >>> env['QUERY_STRING'] = 'x:required='
    >>> pprint.pprint(FormParser(env).parse())
    Traceback (most recent call last):
    ...
    ValueError: No input for required field

Don't leave it empty.

    >>> env['QUERY_STRING'] = 'x:required=123'
    >>> pprint.pprint(FormParser(env).parse())
    {u'x': u'123'}
    >>> env['QUERY_STRING'] = 'x:int:required=123'
    >>> pprint.pprint(FormParser(env).parse())
    {u'x': 123}

Simple Text Handling
--------------------

Use `:tokens` to split the input on whitespace.

    >>> env['QUERY_STRING'] = 'x:tokens=a+b++c%0Ad'
    >>> pprint.pprint(FormParser(env).parse())
    {u'x': [u'a', u'b', u'c', u'd']}

Use `:text` to normalize multiline input.  This is helpful for textarea tags.

    >>> env['QUERY_STRING'] = 'stuff:text=line1%0D%0Aline2%0D%0A'
    >>> pprint.pprint(FormParser(env).parse())
    {u'stuff': u'line1\nline2\n'}

Use `:lines` to convert multiline input to a series of lines.

    >>> env['QUERY_STRING'] = 'x:lines=line1%0D%0A%0D%0Aline2%0D%0A'
    >>> pprint.pprint(FormParser(env).parse())
    {u'x': [u'line1', u'', u'line2']}

Records
-------

The :record suffix produces a record object.

    >>> env['QUERY_STRING'] = 'x.a:int:record=1&x.b:int:record=2'
    >>> form = FormParser(env).parse()
    >>> pprint.pprint(form)
    {u'x': {'a': 1, 'b': 2}}

You can access record values using either attribute or item access.

    >>> x = form['x']
    >>> from zope.httpform.interfaces import IFormRecord
    >>> IFormRecord.providedBy(x)
    True
    >>> x.a
    1
    >>> x['a']
    1

You can use str(record), although repr(record) is more informative.

    >>> str(x)
    '{a: 1, b: 2}'
    >>> repr(x)
    "{'a': 1, 'b': 2}"

Some attribute names would clash with mapping method names and are thus
disallowed.

    >>> env['QUERY_STRING'] = 'x.keys:record='
    >>> FormParser(env).parse()
    Traceback (most recent call last):
    ...
    AttributeError: Illegal record attribute name: keys

Records are useful for address information, for example:

    >>> q = 'shipping.address1:record=Apt+1'
    >>> q += '&shipping.address2:record=75+First+St'
    >>> q += '&billing.address1:record=Apt+29'
    >>> q += '&billing.address2:record=75+First+St'
    >>> env['QUERY_STRING'] = q
    >>> pprint.pprint(FormParser(env).parse())
    {u'billing': {'address1': u'Apt 29', 'address2': u'75 First St'},
     u'shipping': {'address1': u'Apt 1', 'address2': u'75 First St'}}

The :records suffix produces multiple record objects.

    >>> q = 'points.x:float:records=1'
    >>> q += '&points.y:float:records=2'
    >>> q += '&points.x:float:records=11'
    >>> q += '&points.y:float:records=-2'
    >>> env['QUERY_STRING'] = q
    >>> pprint.pprint(FormParser(env).parse())
    {u'points': [{'x': 1.0, 'y': 2.0}, {'x': 11.0, 'y': -2.0}]}

A record can contain a tuple.

    >>> q = 'segment.p0:tuple:record=0'
    >>> q += '&segment.p0:tuple:record=0'
    >>> q += '&segment.p1:tuple:record=10'
    >>> q += '&segment.p1:tuple:record=11'
    >>> env['QUERY_STRING'] = q
    >>> pprint.pprint(FormParser(env).parse())
    {u'segment': {'p0': (u'0', u'0'), 'p1': (u'10', u'11')}}

You can put a list or tuple inside a record list, but you need to use
a non-list record attribute to indiciate the start of each record.
Here we're going to use the record attribute with an empty name to
mark new records.

    >>> q = 'points.color:records:default:int=0'
    >>> q += '&points:records='
    >>> q += '&points.axes:tuple:int:records=0'
    >>> q += '&points.axes:tuple:int:records=0'
    >>> q += '&points.axes:tuple:int:records=0'
    >>> q += '&points.color:int:records='
    >>> q += '&points:records='
    >>> q += '&points.axes:tuple:int:records=1'
    >>> q += '&points.axes:tuple:int:records=2'
    >>> q += '&points.axes:tuple:int:records=3'
    >>> env['QUERY_STRING'] = q
    >>> pprint.pprint(FormParser(env).parse())
    {u'points': [{'': u'', 'axes': (0, 0, 0), 'color': 0},
                 {'': u'', 'axes': (1, 2, 3), 'color': 0}]}

Records can have a default value for each field.

    >>> q = 'friends.birthdate:default:records=unspecified'
    >>> q += '&friends.name:records=Alice'
    >>> q += '&friends.name:records=Bob'
    >>> q += '&friends.name:records=Charlie'
    >>> q += '&friends.birthdate:records=1/1/1'
    >>> env['QUERY_STRING'] = q
    >>> pprint.pprint(FormParser(env).parse())
    {u'friends': [{'birthdate': u'unspecified', 'name': u'Alice'},
                  {'birthdate': u'unspecified', 'name': u'Bob'},
                  {'birthdate': u'1/1/1', 'name': u'Charlie'}]}

There can be a default record.

    >>> q = 'prefs.name:record:default=unnamed'
    >>> q += '&prefs.address:record:default=unknown'
    >>> q += '&prefs.age:int:record:default=100'
    >>> q += '&prefs.address:record=123+Grant+Ave'
    >>> q += '&prefs.age:int:record='
    >>> env['QUERY_STRING'] = q
    >>> pprint.pprint(FormParser(env).parse())
    {u'prefs': {'address': u'123 Grant Ave', 'age': 100, 'name': u'unnamed'}}

Actions
-------

The value of the field named :action is stored as an attribute of
FormParser.  Zope uses the action as the name of a method to call,
but other packages can use the action any other way they need.

By default there is no action:

    >>> env['QUERY_STRING'] = ''
    >>> parser = FormParser(env)
    >>> parser.parse()
    {}
    >>> parser.action is None
    True

Here is an action:

    >>> env['QUERY_STRING'] = 'y:int=1&:action=getX'
    >>> parser = FormParser(env)
    >>> pprint.pprint(parser.parse())
    {u'': u'getX', u'y': 1}
    >>> parser.action
    u'getX'

The value of the action field can be provided by the name of the field.
This is an odd feature, but it's useful for distinguishing between multiple
submit buttons in a form, since HTML forms submit the text on the submit
button as the field value, and the text on the submit button is often
localized.

    >>> env['QUERY_STRING'] = 'stop:action=Parar'
    >>> parser = FormParser(env)
    >>> pprint.pprint(parser.parse())
    {u'stop': u'Parar'}
    >>> parser.action
    u'stop'

The `:method` suffix is a synonym.

    >>> env['QUERY_STRING'] = 'stop:method=Parar'
    >>> parser = FormParser(env)
    >>> pprint.pprint(parser.parse())
    {u'stop': u'Parar'}
    >>> parser.action
    u'stop'

A default action can be provided.

    >>> env['QUERY_STRING'] = ':default_action=next'
    >>> parser = FormParser(env)
    >>> pprint.pprint(parser.parse())
    {u'': u'next'}
    >>> parser.action
    u'next'
    >>> env['QUERY_STRING'] = 'next:default_action=&prev:action='
    >>> parser = FormParser(env)
    >>> pprint.pprint(parser.parse())
    {u'next': u'', u'prev': u''}
    >>> parser.action
    u'prev'

Invalid Input
-------------

Invalid suffixes are counted as part of the field name.  Valid
but unrecognized suffixes get ignored.

    >>> env['QUERY_STRING'] = 'x:0:int=1&y:complex=2'
    >>> pprint.pprint(FormParser(env).parse())
    {u'x:0': 1, u'y': u'2'}

The int, long, and float types require a valid value.

    >>> env['QUERY_STRING'] = 'x:int='
    >>> pprint.pprint(FormParser(env).parse())
    Traceback (most recent call last):
    ...
    ValueError: Empty entry when integer expected

    >>> env['QUERY_STRING'] = 'x:int=z'
    >>> pprint.pprint(FormParser(env).parse())
    Traceback (most recent call last):
    ...
    ValueError: An integer was expected in the value 'z'

    >>> env['QUERY_STRING'] = 'x:long='
    >>> pprint.pprint(FormParser(env).parse())
    Traceback (most recent call last):
    ...
    ValueError: Empty entry when integer expected

    >>> env['QUERY_STRING'] = 'x:long=z'
    >>> pprint.pprint(FormParser(env).parse())
    Traceback (most recent call last):
    ...
    ValueError: A long integer was expected in the value 'z'

    >>> env['QUERY_STRING'] = 'x:float='
    >>> pprint.pprint(FormParser(env).parse())
    Traceback (most recent call last):
    ...
    ValueError: Empty entry when float expected

    >>> env['QUERY_STRING'] = 'x:float=z'
    >>> pprint.pprint(FormParser(env).parse())
    Traceback (most recent call last):
    ...
    ValueError: A float was expected in the value 'z'


URL Encoded POST
----------------

This package accepts POST data in addition to query strings.

    >>> from cStringIO import StringIO
    >>> input_fp = StringIO("x:int=1&y:int=2")
    >>> env = {'REQUEST_METHOD': 'POST',
    ...        'CONTENT_TYPE': 'application/x-www-form-urlencoded',
    ...        'wsgi.input': input_fp}
    >>> pprint.pprint(FormParser(env).parse())
    {u'x': 1, u'y': 2}

The query string is ignored on POST.

    >>> env = {'REQUEST_METHOD': 'POST', 'QUERY_STRING': 'x=1'}
    >>> pprint.pprint(FormParser(env).parse())
    {}

No form parsing is done for content types that don't look like forms.

    >>> input_fp = StringIO("x:int=1&y:int=2")
    >>> env = {'REQUEST_METHOD': 'POST',
    ...        'CONTENT_TYPE': 'text/xml',
    ...        'wsgi.input': input_fp}
    >>> pprint.pprint(FormParser(env).parse())
    {}

File Upload
-----------

Here is an example of what browsers send when users upload a file using
an HTML form:

    >>> content_type = 'multipart/form-data; boundary=AaB03x'
    >>> input_body="""\
    ... --AaB03x
    ... content-disposition: form-data; name="field1:list"
    ...
    ... Joe Blow
    ... --AaB03x
    ... content-disposition: form-data; name="pics"; filename="file1.txt"
    ... Content-Type: text/plain
    ...
    ... I am file1.txt.
    ... --AaB03x--
    ... """

Parse that form.

    >>> env = {'REQUEST_METHOD': 'POST',
    ...        'CONTENT_TYPE': content_type,
    ...        'wsgi.input': StringIO(input_body)}
    >>> form = FormParser(env).parse()
    >>> pprint.pprint(form)
    {u'field1': [u'Joe Blow'],
     u'pics': <zope.httpform.parser.FileUpload object at ...>}

Let's take a good look at the uploaded file.  It has RFC 822 headers and
a content body.

    >>> pics = form['pics']
    >>> from zope.httpform.interfaces import IFileUpload
    >>> IFileUpload.providedBy(pics)
    True
    >>> pics.read()
    'I am file1.txt.'
    >>> pics.filename
    u'file1.txt'
    >>> pics.headers
    <rfc822.Message instance at ...>
    >>> pics.headers['Content-Type']
    'text/plain'
    >>> pprint.pprint(dict(pics.headers))
    {'content-disposition': 'form-data; name="pics"; filename="file1.txt"',
     'content-type': 'text/plain'}

You can use the :string name suffix if you expect the file to be small and
you want just the content body.  The content body is always a byte stream,
not a Unicode string.

    >>> content_type = 'multipart/form-data; boundary=AaB03x'
    >>> input_body="""\
    ... --AaB03x
    ... content-disposition: form-data; name="pics:string"; filename="file1.txt"
    ... Content-Type: text/plain
    ...
    ... I am file1.txt.
    ... --AaB03x--
    ... """
    >>> env = {'REQUEST_METHOD': 'POST',
    ...        'CONTENT_TYPE': content_type,
    ...        'wsgi.input': StringIO(input_body)}
    >>> form = FormParser(env).parse()
    >>> pprint.pprint(form)
    {u'pics': 'I am file1.txt.'}

Send a big file.  (More than 1000 bytes triggers storage to a tempfile.)

    >>> content_type = 'multipart/form-data; boundary=AaB03x'
    >>> input_body="""\
    ... --AaB03x
    ... content-disposition: form-data; name="pics"; filename="file1.txt"
    ... Content-Type: application/octet-stream
    ...
    ... """
    >>> input_body += 30 * '0123456789012345678901234567890123456789'
    >>> input_body += "\n--AaB03x--\n"
    >>> env = {'REQUEST_METHOD': 'POST',
    ...        'CONTENT_TYPE': content_type,
    ...        'wsgi.input': StringIO(input_body)}
    >>> form = FormParser(env).parse()
    >>> pprint.pprint(form)
    {u'pics': <zope.httpform.parser.FileUpload object at ...>}
    >>> data = form['pics'].read()
    >>> len(data)
    1200
    >>> data[:12]
    '012345678901'

