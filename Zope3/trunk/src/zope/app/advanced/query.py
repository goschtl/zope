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
"""Query mechanism

This module contains advanced core query mechanisms. See the
docstrings and interfaces.py for more information.

$Id: query.py,v 1.5 2004/04/01 17:50:19 faassen Exp $
"""

from zope.interface import implements

def advancedQueryMechanism(arguments,action='query',
                           tabs=''):
    """
    Use the advance query mechanism.

    Let's have a look at a typical query session using the mechanism:
    
    >>> exit
    'Use Ctrl-D (i.e. EOF) to exit.'
    >>> quit
    'Use Ctrl-D (i.e. EOF) to exit.'

    This is the typical setup if the query fails:

    >>> helpp
    Traceback (most recent call last):
    ...
    NameError: name 'helpp' is not defined

    Of course, you're not gonna get it to work if you continue on this
    path:

    >>> hello?
    Traceback (most recent call last):
    ...
    SyntaxError: invalid syntax
    >>> mail employee help this doesn't work
    Traceback (most recent call last):
    ...
    SyntaxError: invalid syntax
    >>> what is this???
    Traceback (most recent call last):
    ...
    SyntaxError: invalid syntax
    >>>
    """
    if arguments:
        items=arguments.items()
        # XXX should use a list comprehension
        return (
            "%s\n%s%s" % (
                '<!--#var standard_html_header-->\n%s\n'
                '<form action="%s" method="get">\n'
                '<h2><!--#var document_title--></h2>\n'
                'Enter query parameters:<br>'
                '<table>\n'
                % (tabs,action),
                join(
                    map(
                        lambda a:
                        ('<tr><th>%s</th>\n'
                         '    <td><input name="%s"\n'
                         '               width=30 value="%s">'
                         '</td></tr>'
                         % (nicify(a[0]),
                            (
                                a[1].has_key('type') and
                                ("%s:%s" % (a[0],a[1]['type'])) or
                                a[0]
                                ),
                            a[1].has_key('default') and a[1]['default'] or ''
                            ))
                        , items
                        ),
                '\n'),
                '\n<tr><td colspan=2 align=center>\n'
                '<input type="SUBMIT" name="SUBMIT" value="Submit Query">\n'
                '<!--#if HTTP_REFERER-->\n'
                '  <input type="SUBMIT" name="SUBMIT" value="Cancel">\n'
                '  <INPUT NAME="CANCEL_ACTION" TYPE="HIDDEN"\n'
                '         VALUE="<!--#var HTTP_REFERER-->">\n'
                '<!--#/if HTTP_REFERER-->\n'
                '</td></tr>\n</table>\n</form>\n'
                '<!--#var standard_html_footer-->\n'
                )
            )
    else:
        return (
            '<!--#var standard_html_header-->\n%s\n'
            '<form action="%s" method="get">\n'
            '<h2><!--#var document_title--></h2>\n'
            'This query requires no input.<p>\n'
            '<input type="SUBMIT" name="SUBMIT" value="Submit Query">\n'
            '<!--#if HTTP_REFERER-->\n'
            '  <input type="SUBMIT" name="SUBMIT" value="Cancel">\n'
            '  <INPUT NAME="CANCEL_ACTION" TYPE="HIDDEN"\n'
            '         VALUE="<!--#var HTTP_REFERER-->">\n'
            '<!--#/if HTTP_REFERER-->\n'
            '</td></tr>\n</table>\n</form>\n'
            '<!--#var standard_html_footer-->\n'
            % (tabs, action)
            )

def alternateQueryMechanism(context, adapter, view):
    if result:
        result=join(
            map(
            lambda row, self=self:
            join(map(self.str,row),'\t'),
            result),
            '\n')+'\n'
    else:
        result=''
        
    return (
        "%s\n%s\n%s" % (
        join(map(lambda d: d[0],desc), '\t'),
        join(
        map(
        lambda d, defs=self.defs: "%d%s" % (d[2],defs[d[1]]),
        desc),
        '\t'),
        result,
        )
        )

class AdvancedSuperClass:
    
    def superHasAttr(self,attr):
        obj=self

        seen={}
        vals=[]
        have=seen.has_key
        x=0
        while x < 100:
            try:    set=obj._objects
            except: set=()
            for i in set:
                try:
                    id=i['id']
                    if not have(id):
                        v=getattr(obj,id)
                        if hasattr(v,attr):
                            vals.append(v)
                            seen[id]=1
                except: pass
            try:    obj=obj.aq_parent
            except: return vals
            x=x+1
        return vals

    def superValues(self,t):
        if type(t)==type('s'): t=(t,)

        obj=self
        seen={}
        vals=[]
        have=seen.has_key
        x=0
        while x < 100:
            try:    set=obj._objects
            except: set=()
            for i in set:
                try:
                    id=i['id']
                    if (not have(id)) and (i['meta_type'] in t):
                        vals.append(getattr(obj,id))
                        seen[id]=1
                except: pass
            try:    obj=obj.aq_parent
            except: return vals
            x=x+1
        return vals
