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

$Id: ContentDirective.py,v 1.2 2002/06/10 23:27:46 jim Exp $
"""
from Zope.Configuration.ConfigurationDirectiveInterfaces \
     import INonEmptyDirective
from Zope.Configuration.Action import Action
import Interface

from Zope.App.Security.protectClass \
    import protectLikeUnto, protectName, checkPermission
from Zope.App.ZMI.IGenericCreatorMarker import IGenericCreatorMarker
from Zope.App.ZMI.metaConfigure import provideClass

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
                permission, attributes=None, interface=None):
        """Require a the permission to access a specific aspect"""

        r = []

        if not (interface or attributes):
            # XXX: perhaps raise an error here, as no interface or attributes
            #      were given
            return r

        if interface:
            self.__protectByInterface(interface, permission, r)
        if attributes:
            self.__protectNames(attributes, permission, r)

        return r
        
    def mimic(self, _context, class_):
        """Base security requirements on those of the given class"""
        class_to_mimic = _context.resolve(class_)
        return [
            Action(discriminator=('security:mimic', self.__class, object()),
                   callable=protectLikeUnto,
                   args=(self.__class, class_to_mimic),
                   )
            ]
            
    def allow(self, _context, attributes=None, interface=None):
        """Like require, but with permission_id Zope.Public"""
        return self.require(_context, PublicPermission, attributes, interface)

    def factory(self, _context, permission, title, id=None, description='',
                for_container='', creation_markers=''):
        """Register a zmi factory for this class"""
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

        id = id or self.__id
            
        # note factories are all in one pile, services and content,
        # so addable names must also act as if they were all in the
        # same namespace, despite the service/content division
        return [
            Action(
                discriminator = ('AddableFactory', id),
                callable = provideClass,
                args = ('AddableContent', id, self.__class,
                        permission, title, description, for_container,
                        creation_markers)
                )
            ]



    def __protectByInterface(self, interface, permission_id, r):
        "Set a permission on names in an interface."
        interface = self.__context.resolve(interface)
        for n, d in interface.namesAndDescriptions(1):
            self.__protectName(n, permission_id, r)

    def __protectName(self, name, permission_id, r):
        "Set a permission on a particular name."
        r.append((
            ('security:protectName', self.__class, name),
            protectName, (self.__class, name, permission_id)))
            
    def __protectNames(self, names, permission_id, r):
        "Set a permission on a bunch of names."
        for name in names.split():
            self.__protectName(name.strip(), permission_id, r)


    def __call__(self):
        "Handle empty/simple declaration."
        return ()

    
