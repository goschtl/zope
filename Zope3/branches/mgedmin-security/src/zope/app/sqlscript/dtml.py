##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""
$Id: dtml.py,v 1.2 2004/02/24 16:50:36 philikon Exp $
"""
import sys
from types import StringTypes

from zope.documenttemplate.dt_html import HTML
from zope.documenttemplate.dt_util import ParseError, parse_params, name_param

from interfaces import MissingInput

__metaclass__ = type

valid_type = {'int':    True,
              'float':  True,
              'string': True,
              'nb':     True}.has_key

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
