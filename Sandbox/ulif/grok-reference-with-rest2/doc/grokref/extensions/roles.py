##############################################################################
#
# Copyright (c) 2008 Zope Corporation and Contributors.
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
"""Additional roles for reference documentation.
"""

import re
from docutils import nodes, utils
from docutils.parsers.rst import roles

import addnodes

# default is `literal`
innernodetypes = {
    'ref': nodes.emphasis,
    'term': nodes.emphasis,
    'token': nodes.strong,
}

ws_re = re.compile(r'\s+')
_litvar_re = re.compile('{([^}]+)}')

def xfileref_role(typ, rawtext, text, lineno, inliner, options={}, content=[]):
    text = utils.unescape(text)
    if text[0:1] == '!':
        text = text[1:]
        return [innernodetypes.get(typ, nodes.literal)(
            rawtext, text, classes=['xref'])], []
    pnode = addnodes.pending_xref(rawtext)
    pnode['reftype'] = typ
    # if the first character is a dot, search more specific namespaces first
    # else search builtins first
    if text[0:1] == '.' and \
       typ in ('data', 'exc', 'func', 'class', 'const', 'attr', 'meth'):
        text = text[1:]
        pnode['refspecific'] = True
    pnode['reftarget'] = ws_re.sub((typ == 'term' and ' ' or ''), text)
    pnode += innernodetypes.get(typ, nodes.literal)(rawtext, text,
                                                    classes=['xref'])
    return [pnode], []



def emph_literal_role(typ, rawtext, text, lineno, inliner, options={},
                      content=[]):
    text = utils.unescape(text)
    retnodes = []
    pos = 0
    for m in _litvar_re.finditer(text):
        if m.start() > pos:
            txt = text[pos:m.start()]
            retnodes.append(nodes.literal(txt, txt))
        retnodes.append(nodes.emphasis('', '', nodes.literal(m.group(1),
                                                             m.group(1))))
        pos = m.end()
    if pos < len(text):
        retnodes.append(nodes.literal(text[pos:], text[pos:]))
    return retnodes, []


specific_docroles = {
    'data': xfileref_role,
    'exc': xfileref_role,
    'func': xfileref_role,
    'class': xfileref_role,
    'const': xfileref_role,
    'attr': xfileref_role,
    'meth': xfileref_role,

    'cfunc' : xfileref_role,
    'cdata' : xfileref_role,
    'ctype' : xfileref_role,
    'cmacro' : xfileref_role,

    'mod' : xfileref_role,

    'ref': xfileref_role,
    'token' : xfileref_role,
    'term': xfileref_role,

    'file' : emph_literal_role,
    'samp' : emph_literal_role,
}

for rolename, func in specific_docroles.iteritems():
    roles.register_canonical_role(rolename, func)
