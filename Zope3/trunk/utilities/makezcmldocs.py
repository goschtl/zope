#! /usr/bin/env python2.2
##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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

$Id: makezcmldocs.py,v 1.7 2003/03/21 20:54:02 jim Exp $
"""

from types import UnicodeType, FunctionType, TypeType, ClassType
import os, sys, re
spaces = re.compile(' *')

def format(text, initial):
    lines = [line.rstrip().expandtabs()
             for line in text.rstrip().split('\n')]

    # Remove leading blank lines
    while lines and not lines[0]:
        lines.pop(0)

    # Get minimum indentation
    indent = len(text)
    for line in lines:
        # skip blank lines
        if not line:
            continue
        indent = min(indent, len(spaces.match(line).group()))

    # Now, normalize, by removing the minimum indentation
    lines = [(initial + line[indent:])
             for line in lines]

    return '\n'.join(lines)

# Get Zope3 stuff in the pythonpath.  Note that we use 'here' later as well.
basepath = filter(None, sys.path)
here = os.path.normpath(os.path.join(os.getcwd(),
                                     os.path.split(sys.argv[0])[0]))
root = os.path.split(here)[0]  #We live in the utilities subdirectory
libpython = os.path.join(root, 'src')
sys.path=[libpython] + basepath

# Now for the z3 imports.
from zope.configuration.meta import _directives
from zope.configuration.xmlconfig import XMLConfig
from zope.app import config
from zope.configuration.metametaconfigurefordocgen import _metadataKey

# Some additional useful names.
treeroot = os.path.join(root,'doc','zcml.new')   #Where we put the docs.

def handlerData(handler, metadata):
    """Normalize information about the handler for a directive

    Returns a tuple of a path and a description.  The path is an
    attempt to get something resembling the directory containing
    the zcml defining the directive, by guessing that the meta.zcml
    file is in the same directory as the handler.  THIS NEEDS FIXING.
    If the handler is a method, we return blank, since we have no
    information to base a guess on.  The description is a string
    consiting of the type of the handler (function, method, class,
    type) and either the name (for a method) or the full python
    path to the handler.
    """
    if type(handler)==FunctionType:
        parts = metadata['handler'].split('.')
        path = '.'.join(parts[:-2])
        name = parts[-1]
        typ = 'function'
    elif type(handler)==TypeType:
        path = '.'.join(handler.__module__.split('.')[:-1])
        name = handler.__name__
        typ = 'type'
    elif type(handler)==ClassType:
        path = '.'.join(handler.__module__.split('.')[:-1])
        name = handler.__name__
        typ = 'class'
    elif type(handler)==UnicodeType:
        path = ''
        name = handler
        typ = 'method'
    return path, "%s %s%s" % (typ,path and path+'.' or '',name)

# This should really be refactored so you can see what's actually
# going on here.
def printdirective(outfile, name, handler, registry, level=0):
    global curpath
    if level>10:
        return
    
    fileshortname = outfile.name[len(treeroot)+1:-4]
    ns, name = name
    md = registry[_metadataKey]
    path, handlerstring = handlerData(handler,md)
    if path:
        curpath = path
    outfile.write("%sZCML %s directive\n\n" % (' '*level, name))
    

    initial = ' '*(level+2)
    initial4 = ' '*(level+4)
    initial6 = ' '*(level+6)

    description = md.get('description','')
    if description:
        outfile.write(format(description, initial)+'\n\n')
    else:
        sys.stderr.write("%s in %s has no description\n" % (name, curpath))

    outfile.write(initial+'Attributes\n\n')

    for attr in md['attributes']:
        amd = md['attributes'][attr]
        description = amd.get('description','')
        if 0 and not description:
            sys.stderr.write(("%s in %s has no description " +
                              "for the %s attribute\n") %
                             (name, curpath, attr))
        required = amd.get('required')
        required = (required=='yes' and '(required) ' or required=='no' and
            '(optional) ' or '')

        outfile.write(initial4)
        outfile.write(
            "%s -- %s\n\n%s\n\n"
            % (attr,required, format(description, initial6)))

    if (level<9 and len(registry)>1 or len(registry)==1 and not
            registry.keys()==[_metadataKey]):
        outfile.write(initial+'Subdirectives\n\n')
    for subdir in registry:
        if subdir==_metadataKey: continue
        subs, handler = registry[subdir]
        printdirective(outfile, subdir, handler, subs, level+4)

# The function without a module name is useless.
##     outfile.write("%s  (This directive is handled by by %s. %s)\n\n"
##                   % (' '*level, handlerstring, curpath))


def run(argv=sys.argv):

    # Do global software config for Zope package in docgen mode.
    config(os.path.join(here, 'makezcmldocs.zcml'))

    # Build the meta docs from the contents of the directive registry.
    if not os.path.exists(treeroot):
        os.mkdir(treeroot)
    for directive in _directives:
        ns, name = directive
        ns = ns[7:]
        nspath = os.path.join(treeroot,ns)
        if not os.path.exists(nspath):
            os.makedirs(nspath)
        filepath = os.path.join(nspath,'%s.stx' % name)
        dirfile = open(filepath,'w')
        callable, subs = _directives[directive]
        printdirective(dirfile, directive, callable, subs)


if __name__ == '__main__':
    run()
