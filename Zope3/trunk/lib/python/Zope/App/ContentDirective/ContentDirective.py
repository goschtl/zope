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
""" Register class directive.

$Id: ContentDirective.py,v 1.5 2002/06/23 17:03:40 jim Exp $
"""
from Zope.Configuration.ConfigurationDirectiveInterfaces \
     import INonEmptyDirective
from Zope.ComponentArchitecture import getService
from Zope.Configuration.Exceptions import ConfigurationError
from Zope.Configuration.Action import Action
import Interface
from Zope.App.ComponentArchitecture.ClassFactory import ClassFactory
from Zope.App.Security.protectClass \
    import protectLikeUnto, protectName, checkPermission
from Zope.Security.Proxy import ProxyFactory
from Zope.Security.Checker import NamesChecker

PublicPermission = 'Zope.Public'

class ProtectionDeclarationException(Exception):
    """Security-protection-specific exceptions."""
    pass

class ContentDirective:

    __implements__ = INonEmptyDirective

    def __init__(self, _context, class_):
        self.__id = class_
        self.__class = _context.resolve(class_)
        # not used yet
        #self.__name = class_
        #self.__normalized_name = _context.getNormalizedName(class_)
        self.__context = _context

    def implements(self, _context, interface):
        resolved_interface = _context.resolve(interface)
        return [
            Action(
                discriminator = ('ContentDirective', self.__class, object()),
                callable = Interface.Implements.implements,
                # the last argument is check=1, which causes implements
                # to verify that the class does implement the interface
                args = (self.__class, resolved_interface, 1),
                )
            ]

    def require(self, _context,
                permission=None, attributes=None, interface=None,
                like_class=None):
        """Require a the permission to access a specific aspect"""

        if like_class:
            r = self.__mimic(_context, like_class)
        else:
            r = []

        if not (interface or attributes):
            if r:
                return r
            raise ConfigurationError("Nothing required")

        if not permission:
            raise ConfigurationError("No permission specified")
            

        if interface:
            self.__protectByInterface(interface, permission, r)
        if attributes:
            self.__protectNames(attributes, permission, r)


        return r
        
    def __mimic(self, _context, class_):
        """Base security requirements on those of the given class"""
        class_to_mimic = _context.resolve(class_)
        return [
            Action(discriminator=('mimic', self.__class, object()),
                   callable=protectLikeUnto,
                   args=(self.__class, class_to_mimic),
                   )
            ]
            
    def allow(self, _context, attributes=None, interface=None):
        """Like require, but with permission_id Zope.Public"""
        return self.require(_context, PublicPermission, attributes, interface)



    def __protectByInterface(self, interface, permission_id, r):
        "Set a permission on names in an interface."
        interface = self.__context.resolve(interface)
        for n, d in interface.namesAndDescriptions(1):
            self.__protectName(n, permission_id, r)

    def __protectName(self, name, permission_id, r):
        "Set a permission on a particular name."
        r.append((
            ('protectName', self.__class, name),
            protectName, (self.__class, name, permission_id)))
            
    def __protectNames(self, names, permission_id, r):
        "Set a permission on a bunch of names."
        for name in names.split():
            self.__protectName(name.strip(), permission_id, r)


    def __call__(self):
        "Handle empty/simple declaration."
        return ()


    def factory(self, _context,
                permission=None, title="", id=None, description=''):
        """Register a zmi factory for this class"""

        id = id or self.__id
            
        # note factories are all in one pile, services and content,
        # so addable names must also act as if they were all in the
        # same namespace, despite the service/content division
        return [
            Action(
                discriminator = ('FactoryFromClass', id),
                callable = provideClass,
                args = (id, self.__class,
                        permission, title, description)
                )
            ]
    
def provideClass(id, _class, permission=None,
                 title='', description=''):
    """Provide simple class setup

    - create a component

    - set component permission
    """

    factory = ClassFactory(_class)
    if permission and (permission != 'Zope.Public'):
        # XXX should getInterfaces be public, as below?
        factory = ProxyFactory(factory,
                               NamesChecker(('getInterfaces',),
                                            __call__=permission))

    getService(None, 'Factories').provideFactory(id, factory)


