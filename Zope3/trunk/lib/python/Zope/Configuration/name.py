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
"""Provide configuration object name resolution

$Id: name.py,v 1.2 2002/06/10 23:29:24 jim Exp $
"""

import os
import sys
from types import ModuleType

def resolve(name, package='ZopeProducts', _silly=('__doc__',), _globals={}):
    name = name.strip()
    
    if name.startswith('.'):
        name=package+name

    if name.endswith('.') or name.endswith('+'):
        name = name[:-1]
        repeat = 1
    else:
        repeat = 0

    names=name.split('.')
    last=names[-1]
    mod='.'.join(names[:-1])

    if not mod:
        return __import__(name, _globals, _globals, _silly)
                 
    while 1:
        m=__import__(mod, _globals, _globals, _silly)
        try:
            a=getattr(m, last)
        except AttributeError:
            if not repeat:
                return __import__(name, _globals, _globals, _silly)
                
        else:
            if not repeat or (not isinstance(a, ModuleType)):
                return a
        mod += '.' + last


def getNormalizedName(name, package):
    name=name.strip()
    if name.startswith('.'):
        name=package+name

    if name.endswith('.') or name.endswith('+'):
        name = name[:-1]
        repeat = 1
    else:
        repeat = 0
    name=name.split(".")
    while len(name)>1 and name[-1]==name[-2]:
        name.pop()
        repeat=1
    name=".".join(name)
    if repeat:
        name+="+"
    return name

def path(file='', package = 'ZopeProducts', _silly=('__doc__',), _globals={}):
    try: package = __import__(package, _globals, _globals, _silly)
    except ImportError:
        if file and os.path.abspath(file) == file:
            # The package didn't matter
            return file
        raise
        
    path = os.path.split(package.__file__)[0]
    if file:
        path = os.path.join(path, file)
    return path
