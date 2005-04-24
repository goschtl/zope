##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Pagelet metadconfigure

$Id$
"""
__docformat__ = 'restructuredtext'

import os
import sys

from zope.interface import Interface
from zope.interface import implements

from zope.security.checker import defineChecker
from zope.security.checker import CheckerPublic, Checker

from zope.configuration.exceptions import ConfigurationError

from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from zope.app import zapi
from zope.app.component.metaconfigure import handler
from zope.app.component.interface import provideInterface
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.component.interfaces import IView

from zope.app.pagelet.interfaces import IPageletSlot
from zope.app.pagelet.interfaces import IPagelet



def checkInterface(iface, baseIface):
    if not iface.isOrExtends(baseIface):
        raise ConfigurationError(
            "slot has to implement pagelet.interfaces.IPageletSlot")


def PageletClass(template, weight=0, bases=()):

    frame = sys._getframe(1).f_globals
    
    class_ = type("PageletClass from %s" % template, bases,
                  {'_template':ViewPageTemplateFile(template, frame)
                  ,'_weight':weight})

    return class_



class simplepagelet(object):
    """Pagelet adapter class used in meta directive as a mixin class."""

    implements(IPagelet)

    _weight = 0

    def __init__(self, context, request, view, ignored):
        self.context = context
        self.request = request
        self.view = view

    def __getitem__(self, name):
        """Get the zpt code defined in 'define-macro' by name."""
        return self._template.macros[name]

    def _getWeight (self):
        """The weight of the pagelet."""
        return self._weight

    weight = property(_getWeight)



def pagelet(_context, name, slot, permission, for_=Interface,
            layer=IDefaultBrowserLayer, view=IView, weight=0, template=None):

    required = {}

    # set permission checker
    permission = _handle_permission(permission)

    if not name:
        raise ConfigurationError("Must specify name.")

    if not slot:
        raise ConfigurationError("Must specify a slot interface.")

    if not template:
        raise ConfigurationError("Must specify a template.")

    template = os.path.abspath(str(_context.path(template)))
    if not os.path.isfile(template):
        raise ConfigurationError("No such file", template)

    new_class = PageletClass(template, weight, bases=(simplepagelet, ))

    # set permissions
    for n in ('__getitem__', 'weight'):
        required[n] = permission

    #register interface
    _handle_iface(_context, for_)
    _handle_iface(_context, view)
    _handle_iface(_context, slot)

    # check slot interface
    _handle_check_interface(_context, slot, IPageletSlot)

    # define checker
    defineChecker(new_class, Checker(required))

    # register pagelet
    _context.action(
        discriminator = ('pagelet', for_, layer, view, slot, name),
        callable = handler,
        args = ('provideAdapter',
                (for_, layer, view, slot), IPagelet, name, new_class
                , _context.info),)


def _handle_iface(_context, iface):
    if iface is not None:
        _context.action(
            discriminator = None,
            callable = provideInterface,
            args = ('', iface)
            )

def _handle_check_interface(_context, iface, baseIface):
    if iface is not None and baseIface is not None:
        _context.action(
            discriminator = None,
            callable = checkInterface,
            args = (iface, baseIface)
            )

def _handle_permission(permission):
    if permission == 'zope.Public':
        permission = CheckerPublic
    return permission
