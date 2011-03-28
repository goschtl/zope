##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
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
from zope import interface
import zope.interface.interfaces

def checkConstraint(super, child=None, childDeclaration=None):
    if childDeclaration is None:
        if child is None:
            raise TypeError(
                "Must provide at least one of childDeclaration or child")
        childDeclaration = interface.providedBy(child)
    elif not zope.interface.interfaces.IDeclaration.providedBy(
        childDeclaration):
        childDeclaration = interface.Declaration(childDeclaration)
    __setitem__ = interface.providedBy(super).get('__setitem__')
    if __setitem__ is not None:
        precondition = __setitem__.queryTaggedValue('precondition')
        if precondition is not None:
            if child is not None:
                try:
                    precondition(super, child)
                except interface.Invalid:
                    return False
            try:
                precondition = precondition.declarationConstraint
            except AttributeError:
                pass
            else:
                try:
                    precondition(super, childDeclaration)
                except zope.interface.Invalid:
                    return False

    # check the constraint on childDeclaration.super
    superField = childDeclaration.get('super')
    if superField is not None:
        try:
            validate = superField.validate
        except AttributeError:
            pass
        else:
            try:
                validate(super)
            except zope.interface.Invalid:
                return False

    return True

