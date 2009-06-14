##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""HTTP form parser that supports file uploads, Unicode, and various suffixes.

The FormParser class uses Python's standard ``cgi.FieldStorage`` class.
It converts field names and values to Unicode, handles file uploads in
a graceful manner, and allows field name suffixes that tell the parser
how to handle each field.  The standard suffixes are:

    - ``:int``      -- convert to an integer
    - ``:float``    -- convert to a float
    - ``:long``     -- convert to a long integer
    - ``:string``   -- convert to a string (useful for uploads)
    - ``:required`` -- raise ValueError if the field is not provided
    - ``:tokens``   -- split the input on whitespace characters
    - ``:lines``    -- split multiline input into a list of lines
    - ``:text``     -- normalize line endings of multiline text
    - ``:boolean``  -- true if nonempty, false if empty
    - ``:list``     -- make a list even if there is only one value
    - ``:tuple``    -- make a tuple
    - ``:action``   -- specify the form action
    - ``:method``   -- same as ``:action``
    - ``:default``  -- provide a default value
    - ``:record``   -- generate a record object
    - ``:records``  -- generate a list of record object
    - ``:ignore_empty``   -- discard the field value if it's empty
    - ``:default_action`` -- specifies a default form action
    - ``:default_method`` -- same as ``:default_action``

$Id: $
"""
__docformat__ = 'restructuredtext'

from cgi import FieldStorage
from cStringIO import StringIO
import re
import tempfile
from zope.interface import implements
from zope.interface.common.mapping import IExtendedReadMapping

from zope.httpform.interfaces import IFormParser
from zope.httpform.interfaces import IFormRecord
from zope.httpform.interfaces import IFileUpload
from zope.httpform.typeconv import get_converter

_type_format = re.compile('([a-zA-Z][a-zA-Z0-9_]+|\\.[xy])$')

# Flag Constants
SEQUENCE = 1
DEFAULT = 2
RECORD = 4
RECORDS = 8
REC = RECORD | RECORDS
CONVERTED = 32

def decode_utf8(s):
    """Decode a UTF-8 string"""
    return unicode(s, 'utf-8')

class FormParser(object):
    """Form data parser."""
    implements(IFormParser)

    def __init__(self, env, wsgi_input=None, to_unicode=decode_utf8):
        """Create a form parser for the given WSGI or CGI environment.

        The wsgi_input parameter provides the request input stream.
        If wsgi_input is None (default), the parser tries to get
        the request input stream from 'wsgi.input' in the environment.

        If to_unicode is specified, it is the function to use
        to convert input byte strings to Unicode.  Otherwise, UTF-8
        encoding is assumed.
        """
        self._env = env
        if wsgi_input is None:
            wsgi_input = env.get('wsgi.input')
        self._wsgi_input = wsgi_input
        self._to_unicode = to_unicode

    def parse(self):
        """See IFormParser."""
        self.form = {}
        self.action = None

        method = self._env.get('REQUEST_METHOD', '').upper()
        if method in ('GET', 'HEAD'):
            # Look for a query string instead of an input body
            fp = None
        else:
            # Look for an input body
            fp = self._wsgi_input
            if method == 'POST':
                content_type = self._env.get('CONTENT_TYPE')
                if content_type and not (
                    content_type.startswith('application/x-www-form-urlencoded')
                    or
                    content_type.startswith('multipart/')
                    ):
                    # The WSGI environment does not contain form data.
                    return self.form
        return self._parse_fp(fp)

    def _parse_fp(self, fp):
        # If 'QUERY_STRING' is not present in self._env,
        # FieldStorage will try to get it from sys.argv[1],
        # which is not what we need.
        if 'QUERY_STRING' not in self._env:
            self._env['QUERY_STRING'] = ''

        # If fp is None, FieldStorage might try to read from sys.stdin,
        # which could freeze the process.  Provide an empty body.
        if fp is None:
            fp = StringIO('')

        fs = TempFieldStorage(fp=fp, environ=self._env,
                              keep_blank_values=1)

        fslist = getattr(fs, 'list', None)
        if fslist is not None:
            self._tuple_items = {}
            self._defaults = {}

            # process all entries in the field storage (form)
            for item in fslist:
                self._process_item(item)

            if self._defaults:
                self._insert_defaults()

            if self._tuple_items:
                self._convert_to_tuples()

        return self.form

    def _process_item(self, item):
        """Process item in the field storage."""

        # Check whether this field is a file upload object
        # Note: A field exists for files, even if no filename was
        # passed in and no data was uploaded. Therefore we can only
        # tell by the empty filename that no upload was made.
        key = item.name
        if (hasattr(item, 'file') and hasattr(item, 'filename')
            and hasattr(item,'headers')):
            if (item.file and
                (item.filename is not None and item.filename != ''
                 # RFC 1867 says that all fields get a content-type.
                 # or 'content-type' in map(lower, item.headers.keys())
                 )):
                item = FileUpload(item)
            else:
                item = item.value

        flags = 0
        converter = None
        tuple_item = False

        # Loop through the different types and set
        # the appropriate flags
        # Syntax: var_name:type_name

        # We'll search from the back to the front.
        # We'll do the search in two steps.  First, we'll
        # do a string search, and then we'll check it with
        # a re search.

        while key:
            pos = key.rfind(":")
            if pos < 0:
                break
            match = _type_format.match(key, pos + 1)
            if match is None:
                break

            key, type_name = key[:pos], key[pos + 1:]

            # find the right type converter
            c = get_converter(type_name)

            if c is not None:
                converter = c
                flags |= CONVERTED
            elif type_name == 'list':
                flags |= SEQUENCE
            elif type_name == 'tuple':
                tuple_item = True
                flags |= SEQUENCE
            elif (type_name == 'method' or type_name == 'action'):
                if key:
                    self.action = self._to_unicode(key)
                else:
                    self.action = self._to_unicode(item)
            elif (type_name == 'default_method'
                    or type_name == 'default_action') and not self.action:
                if key:
                    self.action = self._to_unicode(key)
                else:
                    self.action = self._to_unicode(item)
            elif type_name == 'default':
                flags |= DEFAULT
            elif type_name == 'record':
                flags |= RECORD
            elif type_name == 'records':
                flags |= RECORDS
            elif type_name == 'ignore_empty':
                if not item:
                    # skip over empty fields
                    return

        # Make it unicode if not None
        if key is not None:
            key = self._to_unicode(key)

        if isinstance(item, basestring):
            item = self._to_unicode(item)

        if tuple_item:
            self._tuple_items[key] = True

        if flags:
            self._set_item_with_type(key, item, flags, converter)
        else:
            self._set_item_without_type(key, item)

    def _set_item_without_type(self, key, item):
        """Set item value without explicit type."""
        form = self.form
        if key not in form:
            form[key] = item
        else:
            found = form[key]
            if isinstance(found, list):
                found.append(item)
            else:
                form[key] = [found, item]

    def _set_item_with_type(self, key, item, flags, converter):
        """Set item value with explicit type."""
        #Split the key and its attribute
        if flags & REC:
            key, attr = self._split_key(key)

        # defer conversion
        if flags & CONVERTED:
            try:
                item = converter(item)
            except:
                if item or flags & DEFAULT or key not in self._defaults:
                    raise
                item = self._defaults[key]
                if flags & RECORD:
                    item = getattr(item, attr)
                elif flags & RECORDS:
                    item = getattr(item[-1], attr)

        # Determine which dictionary to use
        if flags & DEFAULT:
            form = self._defaults
        else:
            form = self.form

        # Insert in dictionary
        if key not in form:
            if flags & SEQUENCE:
                item = [item]
            if flags & RECORD:
                r = form[key] = Record()
                setattr(r, attr, item)
            elif flags & RECORDS:
                r = Record()
                setattr(r, attr, item)
                form[key] = [r]
            else:
                form[key] = item
        else:
            r = form[key]
            if flags & RECORD:
                if not flags & SEQUENCE:
                    setattr(r, attr, item)
                else:
                    if not hasattr(r, attr):
                        setattr(r, attr, [item])
                    else:
                        getattr(r, attr).append(item)
            elif flags & RECORDS:
                last = r[-1]
                if not hasattr(last, attr):
                    if flags & SEQUENCE:
                        item = [item]
                    setattr(last, attr, item)
                else:
                    if flags & SEQUENCE:
                        getattr(last, attr).append(item)
                    else:
                        new = Record()
                        setattr(new, attr, item)
                        r.append(new)
            else:
                if isinstance(r, list):
                    r.append(item)
                else:
                    form[key] = [r, item]

    def _split_key(self, key):
        """Split the key and its attribute."""
        i = key.rfind(".")
        if i >= 0:
            return key[:i], key[i + 1:]
        return key, ""

    def _convert_to_tuples(self):
        """Convert form values to tuples."""
        form = self.form

        for key in self._tuple_items:
            if key in form:
                form[key] = tuple(form[key])
            else:
                k, attr = self._split_key(key)

                if k in form:
                    item = form[k]
                    if isinstance(item, Record):
                        if hasattr(item, attr):
                            setattr(item, attr, tuple(getattr(item, attr)))
                    else:
                        for v in item:
                            if hasattr(v, attr):
                                setattr(v, attr, tuple(getattr(v, attr)))

    def _insert_defaults(self):
        """Insert defaults into the form dictionary."""
        form = self.form

        for keys, values in self._defaults.iteritems():
            if not keys in form:
                form[keys] = values
            else:
                item = form[keys]
                if isinstance(values, Record):
                    for k, v in values.items():
                        if not hasattr(item, k):
                            setattr(item, k, v)
                elif isinstance(values, list):
                    for val in values:
                        if isinstance(val, Record):
                            for k, v in val.items():
                                for r in item:
                                    if not hasattr(r, k):
                                        setattr(r, k, v)
                        elif not val in item:
                            item.append(val)


class Record(object):
    """A record parsed from a form.  See `IFormRecord`."""
    implements(IFormRecord)

    _attrs = frozenset(IExtendedReadMapping)

    def __getattr__(self, key, default=None):
        if key in self._attrs:
            return getattr(self.__dict__, key)
        raise AttributeError(key)

    def __setattr__(self, name, value):
        if name in self._attrs or name.startswith('_'):
            raise AttributeError("Illegal record attribute name: %s" % name)
        self.__dict__[name] = value

    def __getitem__(self, key):
        return self.__dict__[key]

    def __str__(self):
        items = self.__dict__.items()
        items.sort()
        return "{" + ", ".join(["%s: %s" % item for item in items]) + "}"

    def __repr__(self):
        items = self.__dict__.items()
        items.sort()
        return ("{"
            + ", ".join(["%s: %s" % (repr(key), repr(value))
            for key, value in items]) + "}")


class TempFieldStorage(FieldStorage):
    """FieldStorage that stores uploads in temporary files"""

    def make_file(self, binary=None):
        return tempfile.NamedTemporaryFile('w+b')


class FileUpload(object):
    """Holds an uploaded file. """
    implements(IFileUpload)

    def __init__(self, field_storage):

        f = field_storage.file
        d = self.__dict__
        methods = ['close', 'fileno', 'flush', 'isatty',
            'read', 'readline', 'readlines', 'seek',
            'tell', 'truncate', 'write', 'writelines', 'name']
        for m in methods:
            if hasattr(f, m):
                d[m] = getattr(f, m)

        self.headers = field_storage.headers
        self.filename = unicode(field_storage.filename, 'UTF-8')


def parse(env, wsgi_input=None, to_unicode=decode_utf8):
    """Shortcut for creating a FormParser and calling the parse() method."""
    return FormParser(env, wsgi_input, to_unicode).parse()
