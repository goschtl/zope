##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""\
Inserting optional tests with 'sqlgroup'

    It is sometimes useful to make inputs to an SQL statement
    optinal.  Doing so can be difficult, because not only must the
    test be inserted conditionally, but SQL boolean operators may or
    may not need to be inserted depending on whether other, possibly
    optional, comparisons have been done.  The 'sqlgroup' tag
    automates the conditional insertion of boolean operators.

    The 'sqlgroup' tag is a block tag that has no attributes. It can
    have any number of 'and' and 'or' continuation tags.

    Suppose we want to find all people with a given first or nick name
    and optionally constrain the search by city and minimum and
    maximum age.  Suppose we want all inputs to be optional.  We can
    use DTML source like the following::

      <dtml-sqlgroup>
        <dtml-sqlgroup>
          <dtml-sqltest name column=nick_name type=nb multiple optional>
        <dtml-or>
          <dtml-sqltest name column=first_name type=nb multiple optional>
        </dtml-sqlgroup>
      <dtml-and>
        <dtml-sqltest home_town type=nb optional>
      <dtml-and>
        <dtml-if minimum_age>
           age >= <dtml-sqlvar minimum_age type=int>
        </dtml-if>
      <dtml-and>
        <dtml-if maximum_age>
           age <= <dtml-sqlvar maximum_age type=int>
        </dtml-if>
      </dtml-sqlgroup>

    This example illustrates how groups can be nested to control
    boolean evaluation order.  It also illustrates that the grouping
    facility can also be used with other DTML tags like 'if' tags.

    The 'sqlgroup' tag checks to see if text to be inserted contains
    other than whitespace characters.  If it does, then it is inserted
    with the appropriate boolean operator, as indicated by use of an
    'and' or 'or' tag, otherwise, no text is inserted.

Inserting optional tests with 'sqlgroup'

    It is sometimes useful to make inputs to an SQL statement
    optinal.  Doing so can be difficult, because not only must the
    test be inserted conditionally, but SQL boolean operators may or
    may not need to be inserted depending on whether other, possibly
    optional, comparisons have been done.  The 'sqlgroup' tag
    automates the conditional insertion of boolean operators.

    The 'sqlgroup' tag is a block tag. It can
    have any number of 'and' and 'or' continuation tags.

    The 'sqlgroup' tag has an optional attribure, 'required' to
    specify groups that must include at least one test.  This is
    useful when you want to make sure that a query is qualified, but
    want to be very flexible about how it is qualified.

    Suppose we want to find people with a given first or nick name,
    city or minimum and maximum age.  Suppose we want all inputs to be
    optional, but want to require *some* input.  We can
    use DTML source like the following::

      <dtml-sqlgroup required>
        <dtml-sqlgroup>
          <dtml-sqltest name column=nick_name type=nb multiple optional>
        <dtml-or>
          <dtml-sqltest name column=first_name type=nb multiple optional>
        </dtml-sqlgroup>
      <dtml-and>
        <dtml-sqltest home_town type=nb optional>
      <dtml-and>
        <dtml-if minimum_age>
           age >= <dtml-sqlvar minimum_age type=int>
        </dtml-if>
      <dtml-and>
        <dtml-if maximum_age>
           age <= <dtml-sqlvar maximum_age type=int>
        </dtml-if>
      </dtml-sqlgroup>

    This example illustrates how groups can be nested to control
    boolean evaluation order.  It also illustrates that the grouping
    facility can also be used with other DTML tags like 'if' tags.

    The 'sqlgroup' tag checks to see if text to be inserted contains
    other than whitespace characters.  If it does, then it is inserted
    with the appropriate boolean operator, as indicated by use of an
    'and' or 'or' tag, otherwise, no text is inserted.

Inserting values with the 'sqlvar' tag

    The 'sqlvar' tag is used to type-safely insert values into SQL
    text.  The 'sqlvar' tag is similar to the 'var' tag, except that
    it replaces text formatting parameters with SQL type information.

    The sqlvar tag has the following attributes:

      name -- The name of the variable to insert. As with other
              DTML tags, the 'name=' prefix may be, and usually is,
              ommitted.

      type -- The data type of the value to be inserted.  This
              attribute is required and may be one of 'string',
              'int', 'float', or 'nb'.  The 'nb' data type indicates a
              string that must have a length that is greater than 0.

      optional -- A flag indicating that a value is optional.  If a
                  value is optional and is not provided (or is blank
                  when a non-blank value is expected), then the string
                  'null' is inserted.

    For example, given the tag::

      <dtml-sqlvar x type=nb optional>

    if the value of 'x' is::

      Let\'s do it

    then the text inserted is:

      'Let''s do it'

    however, if x is ommitted or an empty string, then the value
    inserted is 'null'.

$Id: sql.py,v 1.13 2004/02/20 16:57:24 fdrake Exp $
"""

import re
import sys

from types import StringTypes

from persistent import Persistent
from persistent.dict import PersistentDict

from zope.documenttemplate.dt_html import HTML
from zope.documenttemplate.dt_util import ParseError, parse_params, name_param
from zope.interface.common.mapping import IEnumerableMapping

from zope.interface import implements
from zope.component import getService
from zope.app.services.servicenames import Utilities
from zope.app import zapi
from zope.app.cache.caching import getCacheForObj, getLocationForCache
from zope.app.interfaces.content.file import IFileContent
from zope.app.interfaces.content.sql import ISQLScript, MissingInput
from zope.app.interfaces.rdb import IZopeDatabaseAdapter
from zope.app.rdb import queryForResults
from zope.app.container.contained import Contained

unparmre = re.compile(r'([\000- ]*([^\000- ="]+))')
parmre = re.compile(r'([\000- ]*([^\000- ="]+)=([^\000- ="]+))')
qparmre = re.compile(r'([\000- ]*([^\000- ="]+)="([^"]*)")')

valid_type = {'int':1, 'float':1, 'string':1, 'nb': 1}.has_key


class InvalidParameter(Exception):
    pass


class Arguments(PersistentDict):
    """Hold arguments of SQL Script"""

    implements(IEnumerableMapping)


def parseArguments(text, result=None):
    """Parse argument string."""

    # Make some initializations
    if result is None:
        result  = {}

    __traceback_info__ = text

    # search for the first argument assuming a default value (unquoted) was
    # given
    match_object = parmre.match(text)

    if match_object:
        name    = match_object.group(2)
        value   = {'default': match_object.group(3)}
        length  = len(match_object.group(1))

    else:
        # search for an argument having a quoted default value
        match_object = qparmre.match(text)

        if match_object:
            name    = match_object.group(2)
            value   = {'default': match_object.group(3)}
            length  = len(match_object.group(1))

        else:
            # search for an argument without a default value
            match_object = unparmre.match(text)

            if match_object:
                name    = match_object.group(2)
                value   = {}
                length  = len(match_object.group(1))
            else:
                # We are done parsing
                if not text or not text.strip():
                    return Arguments(result)
                raise InvalidParameter, text

    # Find type of argument (int, float, string, ...)
    lt = name.find(':')
    if lt > 0:
        if len(name) > lt+1 and name[lt+1] not in ('"', "'", '='):
            value['type'] = name[lt+1:]
            name = name[:lt]
        else:
            raise InvalidParameter, text

    result[name] = value

    return parseArguments(text[length:], result)


class SQLTest:
    name = 'sqltest'
    optional = multiple = None

    # Some defaults
    sql_delimiter = '\0'

    def sql_quote__(self, v):
        if v.find("\'") >= 0:
            v = "''".join(v.split("\'"))
        return "'%s'" %v

    def __init__(self, args):
        args = parse_params(args, name='', type=None, column=None,
                            multiple=1, optional=1, op=None)
        self.__name__ = name_param(args, 'sqlvar')
        has_key=args.has_key
        if not has_key('type'):
            raise ParseError, ('the type attribute is required', 'sqltest')
        self.type = t = args['type']
        if not valid_type(t):
            raise ParseError, ('invalid type, %s' % t, 'sqltest')
        if has_key('optional'):
            self.optional = args['optional']
        if has_key('multiple'):
            self.multiple = args['multiple']
        if has_key('column'):
            self.column = args['column']
        else: self.column=self.__name__

        # Deal with optional operator specification
        op = '='                        # Default
        if has_key('op'):
            op = args['op']
            # Try to get it from the chart, otherwise use the one provided
            op = comparison_operators.get(op, op)
        self.op = op


    def render(self, md):
        name = self.__name__
        t = self.type
        try:
            v = md[name]
        except KeyError, key:
            if key[0] == name and self.optional:
                return ''
            raise KeyError, key, sys.exc_info()[2]

        if isinstance(v, (list, tuple)):
            if len(v) > 1 and not self.multiple:
                raise 'Multiple Values', (
                    'multiple values are not allowed for <em>%s</em>'
                    % name)
        else:
            v = [v]

        vs = []
        for v in v:
            if not v and isinstance(v, StringTypes) and t != 'string':
                continue
            # XXX Ahh, the code from DT_SQLVar is duplicated here!!!
            if t == 'int':
                try:
                    if isinstance(v, StringTypes):
                        int(v)
                    else:
                        v = str(int(v))
                except ValueError:
                    raise ValueError, (
                        'Invalid integer value for **%s**' %name)

            elif t == 'float':
                if not v and isinstance(v, str):
                    continue
                try:
                    if isinstance(v, StringTypes):
                        float(v)
                    else:
                        v = str(float(v))
                except ValueError:
                    raise ValueError, (
                        'Invalid floating-point value for **%s**' %name)
            else:
                v = str(v)
                v = self.sql_quote__(v)

            vs.append(v)

        if not vs:
            if self.optional:
                return ''
            raise MissingInput, 'No input was provided for **%s**' %name

        if len(vs) > 1:
            vs = ', '.join(map(str, vs))
            return "%s in (%s)" % (self.column,vs)
        return "%s %s %s" % (self.column, self.op, vs[0])

    __call__ = render

# SQL compliant comparison operators
comparison_operators = { 'eq': '=', 'ne': '<>',
                         'lt': '<', 'le': '<=', 'lte': '<=',
                         'gt': '>', 'ge': '>=', 'gte': '>=' }


class SQLGroup:
    blockContinuations = 'and', 'or'
    name = 'sqlgroup'
    required = None
    where = None

    def __init__(self, blocks):
        self.blocks = blocks
        tname, args, section = blocks[0]
        self.__name__ = "%s %s" % (tname, args)
        args = parse_params(args, required=1, where=1)
        if args.has_key(''):
            args[args['']] = 1
        if args.has_key('required'):
            self.required = args['required']
        if args.has_key('where'):
            self.where = args['where']


    def render(self, md):
        result = []
        for tname, args, section in self.blocks:
            __traceback_info__ = tname
            s = section(None, md).strip()
            if s:
                if result:
                    result.append(tname)
                result.append("%s\n" % s)

        if result:
            if len(result) > 1:
                result = "(%s)\n" %(' '.join(result))
            else:
                result = result[0]
            if self.where:
                result = "where\n" + result
            return result

        if self.required:
            raise 'Input Error', 'Not enough input was provided!'

        return ''

    __call__ = render


class SQLVar:
    name = 'sqlvar'

    # Some defaults
    sql_delimiter = '\0'

    def sql_quote__(self, v):
        if v.find("\'") >= 0:
            v = "''".join(v.split("\'"))
        return "'%s'" %v

    def __init__(self, args):
        args = parse_params(args, name='', expr='', type=None, optional=1)

        name, expr = name_param(args, 'sqlvar', 1)
        if expr is None:
            expr = name
        else:
            expr = expr.eval
        self.__name__, self.expr = name, expr

        self.args = args
        if not args.has_key('type'):
            raise ParseError, ('the type attribute is required', 'dtvar')

        t = args['type']
        if not valid_type(t):
            raise ParseError, ('invalid type, %s' % t, 'dtvar')


    def render(self, md):
        name = self.__name__
        args = self.args
        t = args['type']
        try:
            expr = self.expr
            if isinstance(expr, StringTypes):
                v = md[expr]
            else:
                v = expr(md)
        except (KeyError, ValueError):
            if args.has_key('optional') and args['optional']:
                return 'null'
            if not isinstance(expr, StringTypes):
                raise
            raise MissingInput, 'Missing input variable, **%s**' %name

        # XXX Shrug, should these tyoes be really hard coded? What about
        # Dates and other types a DB supports; I think we should make this
        # a plugin.
        if t == 'int':
            try:
                if isinstance(v, StringTypes):
                    int(v)
                else:
                    v = str(int(v))
            except:
                if not v and args.has_key('optional') and args['optional']:
                    return 'null'
                raise ValueError, (
                    'Invalid integer value for **%s**' % name)

        elif t == 'float':
            try:
                if isinstance(v, StringTypes):
                    float(v)
                else:
                    v = str(float(v))
            except ValueError:
                if not v and args.has_key('optional') and args['optional']:
                    return 'null'
                raise ValueError, (
                    'Invalid floating-point value for **%s**' % name)

        else:
            orig_v = v
            v = str(v)
            if (not v or orig_v is None) and t == 'nb':
                if args.has_key('optional') and args['optional']:
                    return 'null'
                else:
                    raise ValueError, (
                        'Invalid empty string value for **%s**' % name)

            v = self.sql_quote__(v)

        return v

    __call__ = render


class SQLDTML(HTML):
    __name__ = 'SQLDTML'

    commands = {}

    for k, v in HTML.commands.items():
        commands[k]=v

    # add the new tags to the DTML
    commands['sqlvar' ] = SQLVar
    commands['sqltest'] = SQLTest
    commands['sqlgroup' ] = SQLGroup


class SQLScript(Persistent, Contained):

    implements(ISQLScript, IFileContent)

    def __init__(self, connectionName='', source='', arguments=''):
        self.template = SQLDTML(source)
        self.connectionName = connectionName
        # In our case arguments should be a string that is parsed
        self.arguments = arguments

    def setArguments(self, arguments):
        assert isinstance(arguments, StringTypes), (
               '"arguments" argument of setArguments() must be a string'
               )
        self._arg_string = arguments
        self._arguments = parseArguments(arguments)

    def getArguments(self):
        'See zope.app.interfaces.content.sql.ISQLScript'
        return self._arguments

    def getArgumentsString(self):
        return self._arg_string

    # See zope.app.interfaces.content.sql.ISQLScript
    arguments = property(getArgumentsString, setArguments)

    def setSource(self, source):
        self.template.munge(source)

    def getSource(self):
        return self.template.read_raw()

    # See zope.app.interfaces.content.sql.ISQLScript
    source = property(getSource, setSource)

    def getTemplate(self):
        'See zope.app.interfaces.content.sql.ISQLScript'
        return self.template

    def _setConnectionName(self, name):
        self._connectionName = name
        cache = getCacheForObj(self)
        location = getLocationForCache(self)

        if cache and location:
            cache.invalidate(location)

    def _getConnectionName(self):
        return self._connectionName

    def getConnection(self):
        name = self.connectionName
        connection = zapi.getUtility(self, IZopeDatabaseAdapter, name)
        return connection()

    # See zope.app.interfaces.content.sql.ISQLScript
    connectionName = property(_getConnectionName, _setConnectionName)

    def __call__(self, **kw):
        'See zope.app.interfaces.rdb'

        # Try to resolve arguments
        arg_values = {}
        missing = []
        for name in self._arguments.keys():
            name = name.encode('UTF-8')
            try:
                # Try to find argument in keywords
                arg_values[name] = kw[name]
            except KeyError:
                # Okay, the first try failed, so let's try to find the default
                arg = self._arguments[name]
                try:
                    arg_values[name] = arg['default']
                except KeyError:
                    # Now the argument might be optional anyways; let's check
                    try:
                        if not arg['optional']:
                            missing.append(name)
                    except KeyError:
                        missing.append(name)

        try:
            connection = self.getConnection()
        except KeyError:
            raise AttributeError, (
                "The database connection '%s' cannot be found." % (
                self.connectionName))

        query = apply(self.template, (), arg_values)
        cache = getCacheForObj(self)
        location = getLocationForCache(self)
        if cache and location:
            _marker = object()
            result = cache.query(location, {'query': query}, default=_marker)
            if result is not _marker:
                return result
        result = queryForResults(connection, query)
        if cache and location:
            cache.set(result, location, {'query': query})
        return result


valid_type = {'int':1, 'float':1, 'string':1, 'nb': 1}.has_key
