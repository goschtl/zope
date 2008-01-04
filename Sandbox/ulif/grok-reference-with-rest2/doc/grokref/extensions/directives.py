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
"""
Additional directives for reference documentation.
"""
import re
from docutils.parsers.rst import directives, roles
import addnodes

# ------ functions to parse a Python or C signature and create desc_* nodes.
# ------ also used for parameters like '*args', '**kw'.

py_sig_re = re.compile(r'''^([\w.]*\.)?        # class names
                           (\w+)  \s*          # thing name
                           (?: \((.*)\) )? $   # optionally arguments
                        ''', re.VERBOSE)
py_paramlist_re = re.compile(r'([\[\],])')  # split at '[', ']' and ','


def parse_py_signature(signode, sig, desctype):
    """
    Transform a python signature into RST nodes.
    Return (fully qualified name of the thing, classname if any).

    If inside a class, the current class name is handled intelligently:
    * it is stripped from the displayed name if present
    * it is added to the full name (return value) if not present
    """
    m = py_sig_re.match(sig)
    if m is None: raise ValueError
    classname, name, arglist = m.groups()
    fullname = classname and classname + name or name

    signode += addnodes.desc_classname(classname, classname)

    signode += addnodes.desc_name(name, name)
    if not arglist:
        if desctype in ('function', 'method'):
            # for callables, add an empty parameter list
            signode += addnodes.desc_parameterlist()
        return fullname, classname
    signode += addnodes.desc_parameterlist()

    stack = [signode[-1]]
    for token in py_paramlist_re.split(arglist):
        if token == '[':
            opt = addnodes.desc_optional()
            stack[-1] += opt
            stack.append(opt)
        elif token == ']':
            try: stack.pop()
            except IndexError: raise ValueError
        elif not token or token == ',' or token.isspace():
            pass
        else:
            token = token.strip()
            stack[-1] += addnodes.desc_parameter(token, token)
    if len(stack) != 1: raise ValueError
    return fullname, classname



def desc_directive(desctype, arguments, options, content, lineno,
                   content_offset, block_text, state, state_machine):
    node = addnodes.desc()
    node['desctype'] = desctype

    noindex = ('noindex' in options)
    signatures = map(lambda s: s.strip(), arguments[0].split('\n'))
    names = []
    clsname = None
    for i, sig in enumerate(signatures):
        # add a signature node for each signature in the current unit
        # and add a reference target for it
        sig = sig.strip()
        signode = addnodes.desc_signature(sig, '')
        signode['first'] = False
        node.append(signode)
        try:
            if desctype in ('function', 'data', 'class', 'exception',
                            'method', 'attribute'):
                name, clsname = parse_py_signature(signode, sig, desctype)
            elif desctype in ('cfunction', 'cmember', 'cmacro', 'ctype',
                              'cvar'):
                name = parse_c_signature(signode, sig, desctype)
            elif desctype == 'opcode':
                name = parse_opcode_signature(signode, sig, desctype)
            else:
                # describe: use generic fallback
                raise ValueError
        except ValueError, err:
            signode.clear()
            signode += addnodes.desc_name(sig, sig)
            continue
        # we don't want an index entry here
        # only add target and index entry if this is the first
        # description of the function name in this desc block
        if not noindex and name not in names:
            fullname = name
            # note target
            if fullname not in state.document.ids:
                signode['names'].append(fullname)
                signode['ids'].append(fullname)
                signode['first'] = (not names)
                state.document.note_explicit_target(signode)
            names.append(name)

    subnode = addnodes.desc_content()
    # needed for automatic qualification of members
    clsname_set = False
    if desctype == 'class' and names:
        clsname_set = True
    state.nested_parse(content, content_offset, subnode)
    node.append(subnode)
    return [node]

desc_directive.content = 1
desc_directive.arguments = (1, 0, 1)
desc_directive.options = {'noindex': directives.flag}

desctypes = [
    # the Python ones
    'function',
]

for name in desctypes:
    directives.register_directive(name, desc_directive)

