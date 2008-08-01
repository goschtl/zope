##############################################################################
#
# Copyright (c) 2006-2007 Zope Corporation and Contributors.
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
"""Grok utility functions.
"""
from martian.error import GrokError
from zope.component import queryUtility
from zope.security.checker import NamesChecker, defineChecker
from zope.security.interfaces import IPermission
from zope.app.security.protectclass import protectName
from zope.app.security.protectclass import protectSetAttribute

def protect_getattr(class_, name, permission=None):
    # Define an attribute checker using zope.app.security's
    # protectName that defaults to the 'zope.Public' permission when
    # it's not been given and makes sure the permission has actually
    # been defined when it has.
    if permission is None:
        permission = 'zope.Public'
    else:
        check_permission(class_, permission)

    protectName(class_, name, permission)

def protect_setattr(class_, name, permission=None):
    # Define a set attribute checker.  If permission is not supplied,
    # it defaults to 'zope.Pubic'.  If a permission has been supplied,
    # we make sure the permission has actually been defined.
    if permission is None:
        permission = 'zope.Public'
    else:
        check_permission(class_, permission)

    protectSetAttribute(class_, name, permission)

def make_checker(factory, view_factory, permission, method_names=None):
    """Make a checker for a view_factory associated with factory.

    These could be one and the same for normal views, or different
    in case we make method-based views such as for JSON and XMLRPC.
    """
    if method_names is None:
        method_names = ['__call__']
    if permission is not None:
        check_permission(factory, permission)
    if permission is None or permission == 'zope.Public':
        checker = NamesChecker(method_names)
    else:
        checker = NamesChecker(method_names, permission)
    defineChecker(view_factory, checker)

def check_permission(factory, permission):
    """Check whether a permission is defined.

    If not, raise error for factory.
    """
    if queryUtility(IPermission, name=permission) is None:
       raise GrokError('Undefined permission %r in %r. Use '
                       'grok.Permission first.'
                       % (permission, factory), factory)
