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
from zope.security.checker import getCheckerForInstancesOf
from zope.security.checker import Checker, CheckerPublic

def protect_name(class_, name, permission=None):
    # Define an attribute checker using zope.app.security's
    # protectName that defaults to the 'zope.Public' permission when
    # it's not been given and makes sure the permission has actually
    # been defined when it has.
    if permission is None:
        permission = 'zope.Public'
    else:
        check_permission(class_, permission)

    # The rest of this function is a verbatim copy of
    # zope.app.security.protectclass.protectName.  Unfortunately,
    # zope.app.security pretty much pulls in the whole universe which
    # we'd like to avoid for this simple, barebones package.
    checker = getCheckerForInstancesOf(class_)
    if checker is None:
        checker = Checker({}, {})
        defineChecker(class_, checker)

    if permission == 'zope.Public':
        # Translate public permission to CheckerPublic
        permission = CheckerPublic

    # We know a dictionary was used because we set it
    protections = checker.get_permissions
    protections[name] = permission

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
