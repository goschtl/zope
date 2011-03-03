##############################################################################
#
# Copyright (c) 2001, 2002 Zope Foundation and Contributors.
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
"""Placeless Test Setup
"""

# HACK to make sure basicmost event subscriber is installed
import zope.component
import zope.component.event
import zope.component.registry

# we really don't need special setup now:
from zope.testing.cleanup import CleanUp as PlacelessSetup


def setUp(test=None):
    PlacelessSetup().setUp()


def tearDown(test=None):
    PlacelessSetup().tearDown()


class RegistryStack(object):

    def __init__(self):
        self.stack = []
        self.original_hook = None

    def __call__(self, context=None):
        new = self.stack[-1]
        if self.original_hook:
            original = self.original_hook(context)
        else:
            original = zope.component.getGlobalSiteManager()

        if not self.find_in_bases(new, original):
            bases = (new, original)
            new = zope.component.registry.Components(
                name='wraps %r' % list(bases), bases=bases)
        return new

    def sethook(self, newimplementation):
        self.original_hook = newimplementation
        self.original_sethook(self)

    def find_in_bases(self, haystack, needle):
        if needle in haystack.__bases__:
            return True
        for base in haystack.__bases__:
            if self.find_in_bases(base, needle):
                return True
        return False

    def push(self, item):
        self.stack.append(item)

    def pop(self):
        return self.stack.pop()

    def __len__(self):
        return len(self.stack)

_registry_stack = RegistryStack()


def push_registry():
    if not hasattr(_registry_stack, 'original_sethook'):
        _registry_stack.original_sethook = (
            zope.component.getSiteManager.sethook)
    _make_sethook_overridable()

    current = zope.component.getSiteManager()
    new = zope.component.registry.Components(
        name='wraps %r' % current, bases=(current,))
    _registry_stack.push(new)

    if zope.component.getSiteManager.sethook != _registry_stack.sethook:
        current_hook = zope.component.getSiteManager.sethook(_registry_stack)
        _registry_stack.sethook(current_hook)
        zope.component.getSiteManager.sethook = _registry_stack.sethook


def pop_registry():
    _registry_stack.pop()

    if not _registry_stack:
        zope.component.getSiteManager.sethook(_registry_stack.original_hook)
        zope.component.getSiteManager = _original_getsitemanager
        zope.component.getSiteManager.sethook(_registry_stack.original_hook)
        del _registry_stack.original_sethook


_original_getsitemanager = zope.component.getSiteManager


def _make_sethook_overridable():
    # XXX Why oh why does everything have to be locked down so much?? We need
    # to override sethook for the registry stacking, but neither zope.hookable
    # nor zope.component.hookable allow us to do so. Herewith, a copy&pasted
    # zope.component.hookable, only without the slots. *sigh*

    class overridably_hookable(object):
        original = property(lambda self: self.__original,)
        implementation = property(lambda self: self.__implementation,)

        def __init__(self, implementation):
            self.__original = self.__implementation = implementation

        def sethook(self, newimplementation):
            (old, self.__implementation) = (
                self.__implementation, newimplementation)
            return old

        def reset(self):
            self.__implementation = self.__original

        def __call__(self, *args, **kw):
            return self.__implementation(*args, **kw)

    try:
        import zope.hookable
        hook_module = zope.hookable
    except ImportError:
        import zope.component.hookable
        hook_module = zope.component.hookable

    if isinstance(zope.component.getSiteManager,
                  getattr(hook_module, 'hookable')):
        global _original_getsitemanager
        _original_getsitemanager = zope.component.getSiteManager
        zope.component.getSiteManager = overridably_hookable(
            zope.component.getSiteManager.implementation)

