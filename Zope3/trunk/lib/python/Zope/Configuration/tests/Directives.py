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
Test class for use by test modules

$Id: Directives.py,v 1.3 2002/09/01 18:29:58 rdmurray Exp $
"""

from Zope.Configuration.INonEmptyDirective import INonEmptyDirective

protections=[]

class protectClass:

    __implements__ = INonEmptyDirective

    def __init__(self, _context, name, permission=None, names=None):
        self._name=name
        self._permission=permission
        self._names=names
        self._children=[]
        self.__context = _context

    def __call__(self):
        if not self._children:
            p = self._name, self._permission, self._names
            d = self._name, self._names
            return [(d, protections.append, (p,))]
        else:
            return ()
            
    def protect(self, _context, permission=None, names=None):
        if permission is None: permission=self._permission
        if permission is None: raise 'no perm'
        p=self._name, permission, names
        d=self._name, names
        self._children.append(p)
        return [(d, protections.append, (p,))]

done = []

def doit(_context, name):
    return [('d', done.append, (name,))]

def clearDirectives():
    del protections[:]
    del done[:]

# Register our cleanup with Testing.CleanUp to make writing unit tests simpler.
from Zope.Testing.CleanUp import addCleanUp
addCleanUp(clearDirectives)
del addCleanUp
