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
"""Inserting values with the 'sqlvar' tag

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

$Id: DT_SQLVar.py,v 1.1 2002/07/11 00:03:18 srichter Exp $
"""
from Zope.DocumentTemplate.DT_Util import ParseError, parse_params, name_param
from types import StringTypes


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
        except:
            if args.has_key('optional') and args['optional']:
                return 'null'
            if not isinstance(expr, StringTypes):
                raise
            raise ('Missing Input',
                   'Missing input variable, **%s**' % name)

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
            except:
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


valid_type = {'int':1, 'float':1, 'string':1, 'nb': 1}.has_key
