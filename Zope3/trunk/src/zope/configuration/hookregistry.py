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
$Id: hookregistry.py,v 1.2 2002/12/25 14:13:33 jim Exp $
"""

from types import ModuleType
from zope.exceptions import DuplicationError, NotFoundError, ZopeError
from zope.configuration import name

class MissingHookableError(NotFoundError):
    """the stated hook has not been registered"""

class DuplicateHookError(DuplicationError):
    """an implementation for the given hook has already been registered"""

class BadHookableError(ZopeError):
    """hookable cannot be found or is not usable"""

class BadHookError(ZopeError):
    """hook cannot be set"""

class HookRegistry:
    def __init__(self):
        self._reg = {}

    def addHookable(self, hname):
        if hname in self._reg:
            raise DuplicationError(hname)
        try:
            defaultimpl = name.resolve(hname)
        except ImportError:
            raise BadHookableError("hookable %s cannot be found" % hname)

        parent, last=self._getParentAndLast(hname)
        implfunc="%s_hook" % last

        if getattr(parent, implfunc, self) is self:
            raise BadHookableError(
                """default hookable implementation (%s) cannot be found;
                note it must be in the same module as the hookable""" %
                implfunc)

        self._reg[hname] = 0

    def addHook(self, hookablename, hookname):

        if not (hookablename in self._reg):
            raise MissingHookableError(hookablename)
        if self._reg[hookablename]:
            raise DuplicateHookError(hookablename, hookname)
        try:
            implementation = name.resolve(hookname)
        except ImportError:
            raise BadHookError('cannot find implementation', hookname)
        try:
            hookableDefault=name.resolve(hookablename)
        except:
            raise BadHookableError(
                'hookable cannot be found, but was found earlier: '
                'some code has probably masked the hookable',
                hookablename)

        # This won't work as is: I'd have to create a NumberTypes and do
        # various annoying checks
        #if type(implementation) is not type (hookableDefault):
        #    raise BadHookError(
        #        'hook and hookable must be same type')

        # if they are functions, could check to see if signature is same
        # (somewhat tricky because functions and methods could be
        # interchangable but would have a different signature because
        # of 'self')

        # for now I'll leave both of the above to the sanity of the site
        # configuration manager...

        # find and import immediate parent

        parent,last = self._getParentAndLast(hookablename)

        # set parent.last to implementation
        setattr(parent, "%s_hook" % last, implementation)

        self._reg[hookablename] = hookname

    def _getParentAndLast(self, hookablename):
        if hookablename.endswith('.') or hookablename.endswith('+'):
            hookablename = hookablename[:-1]
            repeat = 1
        else:
            repeat = 0
        names = hookablename.split(".")
        last = names.pop()
        importname = ".".join(names)
        if not importname:
            if not repeat:
                raise BadHookableError(
                    'hookable cannot be on top level of Python namespace',
                    hookablename)
            importname = last
        parent = __import__(importname, {}, {}, ('__doc__',))
        child = getattr(parent, last, self)
        if child is self:
            raise BadHookableError(
                'hookable cannot be on top level of Python namespace',
                hookablename)
        while repeat:
            grand = getattr(child, last, self)
            if grand is self:
                break
            parent = child
            child = grand

        if type(parent) is not ModuleType:
            raise BadHookableError("parent of hookable must be a module")

        return parent, last

    def getHooked(self):
        return [(key, self._reg[key])
                for key in self._reg
                if self._reg[key]]

    def getUnhooked(self):
        return [(key, self._reg[key])
                for key in self._reg
                if not self._reg[key]]

    def getHookables(self):
        return [(key, self._reg[key])
                for key in self._reg]
