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
""" ZMI Addable Registration

$Id: metaConfigure.py,v 1.2 2002/06/10 23:28:19 jim Exp $
"""
from Zope.Configuration.Action import Action
from Zope.ComponentArchitecture import getService
from IGenericCreatorMarker import IGenericCreatorMarker
from Zope.Security.Checker import NamesChecker, CheckerPublic, ProxyFactory
from ClassFactory import ClassFactory

def provideClass(registry, qualified_name, _class, permission,
                 title, description='', for_container=None,
                 creation_markers=None):
    """Provide simple class setup

    - create a component

    - Register as addable

    - register a factory

    - set component permission
    """
    factory = ClassFactory(_class)
    if permission and (permission != 'Zope.Public'):
        # XXX should getInterfaces be public, as below?
        factory = ProxyFactory(factory,
                               NamesChecker(('getInterfaces',),
                                            __call__=permission))
    getService(None, 'Factories').provideFactory(qualified_name, factory)
    registry = getService(None, registry)
    registry.provideAddable(qualified_name, title, description,
                            for_container, creation_markers)


def ServiceClassDir(_context, id, class_, permission, title,
                    description='', for_container='',
                    creation_markers=''):
    if for_container:
        for_container = tuple([_context.resolve(cls)
                               for cls in for_container.split()])
    else:
        for_container = None

    if creation_markers:
        creation_markers = tuple([_context.resolve(name)
                                  for name in creation_markers.split()])
    else:
        creation_markers = (IGenericCreatorMarker,)
        
    # note factories are all in one pile, services and content,
    # so addable names must also act as if they were all in the
    # same namespace, despite the service/content division        
    return [
        Action(
            discriminator = ('AddableFactory', id),
            callable = provideClass,
            args = ('AddableServices', id, _context.resolve(class_),
                    permission, title, description, for_container,
                    creation_markers)
             )
        ]

