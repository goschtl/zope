##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Make assertions about permissions needed to access class instances
attributes

$Id$
"""
from zope.security.checker import defineChecker, getCheckerForInstancesOf
from zope.security.checker import Checker, CheckerPublic

from permission import checkPermission


def protectName(class_, name, permission):
    """Set a permission on a particular name."""

    checker = getCheckerForInstancesOf(class_)
    if checker is None:
        checker = Checker({}, {})
        defineChecker(class_, checker)

    if permission == 'zope.Public':
        # Translate public permission to CheckerPublic
        permission = CheckerPublic

    # We know a dictionart get method was used because we set it
    protections = checker.get_permissions
    protections[name] = permission

def protectSetAttribute(class_, name, permission):
    """Set a permission on a particular name."""

    checker = getCheckerForInstancesOf(class_)
    if checker is None:
        checker = Checker({}, {})
        defineChecker(class_, checker)

    if permission == 'zope.Public':
        # Translate public permission to CheckerPublic
        permission = CheckerPublic

    # We know a dictionart get method was used because we set it
    protections = checker.set_permissions
    protections[name] = permission

def protectLikeUnto(class_, like_unto):
    """Use the protections from like_unto for class_"""

    unto_checker = getCheckerForInstancesOf(like_unto)
    if unto_checker is None:
        return

    # We know a dictionart get method was used because we set it
    unto_get_protections = unto_checker.get_permissions
    unto_set_protections = unto_checker.set_permissions

    checker = getCheckerForInstancesOf(class_)
    if checker is None:
        checker = Checker({}, {})
        defineChecker(class_, checker)

    # OK, so it's a hack.
    get_protections = checker.get_permissions
    for name in unto_get_protections:
        get_protections[name] = unto_get_protections[name]

    set_protections = checker.set_permissions
    for name in unto_set_protections:
        set_protections[name] = unto_set_protections[name]
