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
"""Helper Utility to wrap a text to a set width of characters

$Id: docutils.py,v 1.1 2004/01/22 23:53:15 srichter Exp $
"""
import re

para_sep = re.compile('\n{2,}')
whitespace=re.compile('[ \t\n\r]+')

def wrap(text, width=78, indent=0):
    """ """
    paras = para_sep.split(text.strip())

    new_paras = []
    for par in paras:
	words= filter(None, whitespace.split(par))
        
        lines = []
        line = []
        length = indent
        for word in words:
            if length + len(word) + 1 <= width:
                line.append(word)
                length += len(word) + 1
            else:
                lines.append(' '*indent + ' '.join(line))
                line = []
                length = indent

        lines.append(' '*indent + ' '.join(line))
        
        new_paras.append('\n'.join(lines))

    return '\n\n'.join(new_paras) + '\n\n'


def makeDocStructures(context):
    """ """
    namespaces = {}
    subdirs = {}
    for (namespace, name), schema, usedIn, info, parent in context._docRegistry:
        if not parent:
            ns_entry = namespaces.setdefault(namespace, {})
            ns_entry[name] = (schema, info)
        else:
            sd_entry = subdirs.setdefault((parent.namespace, parent.name), [])
            sd_entry.append((namespace, name, schema, info))
    return namespaces, subdirs    
