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
from os import path
import re
from docutils.parsers.rst import directives, roles
from docutils.parsers.rst.directives import admonitions

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
    """
    m = py_sig_re.match(sig)
    if m is None: raise ValueError
    classname, name, arglist = m.groups()
    
    fullname = classname and classname + name or name
    if classname is not None:
        signode += nodes.strong(classname, classname)
    signode += nodes.strong(name, name)
    if not arglist:
        if desctype in ('function', 'method'):
            # for callables, add an empty parameter list
            signode += nodes.inline(u'()', u'()')
        return fullname, classname
    signode += nodes.inline()

    paramlist = py_paramlist_re.split(arglist)
    if len(paramlist):
        signode += nodes.inline('(', '(')
    stack = [signode[-1]]
    for token in paramlist:
        if token == '[':
            opt = nodes.inline('[', '[')
            stack[-1] += opt
            stack.append(opt)
        elif token == ']':
            stack[-1] += nodes.inline(token, token)
            try: stack.pop()
            except IndexError: raise ValueError
        elif not token or token == ',' or token.isspace():
            if token:
                if token == ',':
                    stack[-1] += nodes.inline(', ', ', ')
                else:
                    stack[-1] += nodes.inline(token, token)
            pass
        else:
            token = token.strip()
            paramnode = nodes.emphasis(token, token)
            stack[-1] += paramnode
    if len(stack) != 1: raise ValueError
    if len(paramlist):
        signode += nodes.inline(')', ')')
    return fullname, classname


# ------ toctree directive ----------------------------------------------------
from docutils import nodes
def toctree_directive(name, arguments, options, content, lineno,
                      content_offset, block_text, state, state_machine):
    # We currently ignore toctrees, i.e. we set them up as comment nodes.
    settings = state.document.settings
    filename = settings._source
    dirname = path.dirname(filename)

    subnode = nodes.comment()
    includefiles = filter(None, content)
    # normalize filenames
    includefiles = map(lambda x: path.normpath(path.join(dirname, x)),
                       includefiles)
    subnode['includefiles'] = includefiles
    subnode['maxdepth'] = options.get('maxdepth', -1)
    return [subnode]


toctree_directive.content = 1
toctree_directive.options = {'maxdepth': int}
directives.register_directive('toctree', toctree_directive)


# ------ desc directive ----------------------------------------------------

def desc_directive(desctype, arguments, options, content, lineno,
                   content_offset, block_text, state, state_machine):
    node = nodes.admonition()
    node['classes'] += ['desc-' + str(desctype)]
    signatures = map(lambda s: s.strip(), arguments[0].split('\n'))
    node['desctype'] = desctype
    names = []
    for i, sig in enumerate(signatures):
        sig = sig.strip()
        signode = nodes.inline(sig, '')
        signode['first'] = False
        node.append(signode)
        try:
            if desctype in ('function', 'data', 'class', 'exception',
                            'method', 'attribute'):
                name, clsname = parse_py_signature(signode, sig, desctype)
        except ValueError, err:
            signode.clear()
            signode += nodes.inline(sig, sig)
            continue
    subnode = nodes.container()
    # needed for automatic qualification of members
    state.nested_parse(content, content_offset, subnode)
    node.append(subnode)
    return [node]

desc_directive.content = 1
desc_directive.arguments = (1, 0, 1)
desc_directive.options = {'noindex': directives.flag}

desctypes = [
    # the Python ones
    'function',
    'data',
    'class',
    'method',
    'attribute',
    'exception',
    # the generic ones
    'cmdoption', # for command line options
    'envvar', # for environment variables
    'describe',
]

for name in desctypes:
    directives.register_directive(name, desc_directive)


# ------ see also -------------------------------------------------------------

def seealso_directive(name, arguments, options, content, lineno,
                      content_offset, block_text, state, state_machine):
    """A directive to indicate, that other things are of interest as
    well.
    """
    # Add a marker, which type of versioninfo we build.  This way, in
    # HTML output there will be a class='seealso' attribution.
    options['class'] = [str(name)]

    rv = admonitions.make_admonition(
        nodes.admonition, name, ['See also'], options, content,
        lineno, content_offset, block_text, state, state_machine)
    return rv

seealso_directive.content = 1
seealso_directive.arguments = (0, 0, 0)
directives.register_directive('seealso', seealso_directive)



# ------ versionadded/versionchanged ------------------------------------------

def version_directive(name, arguments, options, content, lineno,
                      content_offset, block_text, state, state_machine):
    """A directive to indicate version related modifications.
    """
    node = nodes.admonition()

    # sphinx stuff. Do we really need it?
    node['type'] = name
    node['version'] = arguments[0]

    # Construct a message...
    if name == 'versionchanged':
        text = u'Changed in version %s: ' % (node['version'])
    elif name == 'versionadded':
        text = u'Added in version %s: ' % (node['version'])
    elif name == 'deprecated':
        text = u'Deprecated from version %s: '% (node['version'])
    else:
        text = u'%s %s: ' % (name, arguments[0])
    arguments[0] = text
    
    # Add a marker, which type of versioninfo we build.  This way, in
    # HTML output there will be a class='versionchanged' attribution.
    options['class'] = [str(name)]

    # Create a admonition node...
    rv = admonitions.make_admonition(
        nodes.admonition, name, arguments, options, content,
        lineno, content_offset, block_text, state, state_machine)
    return rv

version_directive.arguments = (1, 1, 1)
version_directive.content = 1

directives.register_directive('deprecated', version_directive)
directives.register_directive('versionadded', version_directive)
directives.register_directive('versionchanged', version_directive)
