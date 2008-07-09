##############################################################################
#
# Copyright (c) 2008 Zope Corporation and Contributors.
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
"""Interfaces for zope.introspector.
"""
from zope import interface

class IIntrospectorBaseClasses(interface.Interface):
    priority = interface.Attribute(
        "Directive for use in description providers")
    DescriptionProvider = interface.Attribute(
        "A component that delivers a suitable description object "
        "for certain kinds of objects."
        )
    ObjectInfo = interface.Attribute("Basic Object Information")
    ModuleInfo = interface.Attribute("Information about a module")
    PackageInfo = interface.Attribute("Information about a package")
    TypeInfo = interface.Attribute("Information about a basic type")
    UtilityInfo = interface.Attribute("Utilities an object can access")
    RegistryInfo = interface.Attribute(
        "Information about the component registry")

class IIntrospectorAPI(IIntrospectorBaseClasses):
    """The API of zope.introspector.
    """
    pass

class IObjectInfo(interface.Interface):
    """Information about simple types.
    """
    def getType():
        """Get the type of the object handled here.
        """

class IModuleInfo(interface.Interface):
    """Information about modules.
    """
    pass

class IPackageInfo(interface.Interface):
    """Information about packages.
    """
    def getPackageFiles():
        """Get the package files contained in a package.
        """

class IUtilityInfo(interface.Interface):
    """Information about utilities available to an object.
    """
    def getAllUtilities():
        """Get all utilities available to an object.
        """

class ITypeInfo(interface.Interface):
    """Information about types.
    """
    pass

class IRegistryInfo(interface.Interface):
    """Keeps information about the Component registry.
    """
    def getAllRegistrations(registry):
        """ Returns a list of everything registered in the component registry. 
        """
    
    def getAllUtilities(registry):
        """ Returns a list of all utilities registered in the
        component registery.
        """
        
    def getAllAdapters(registry):
        """ Returns a list of all adapters registered in the component
        registery.
        """
    
    def getAllHandlers(registry):
        """ Returns a list of all handlers registered in the component
        registery.
        """
        
    def getAllSubscriptionAdapters(registry):
        """ Returns a list of all handlers registered in the component
        registery.
        """
        
    def getRegistrationsForInterface(searchString, types):
        """ Searches the component registry for any interface with
            searchString in the name...

            Returns a list of component objects.
        """
        
    def getAllInterfaces():
        """ Returns a dictionary with all interfaces...
            {'zope': 
                    {'app':
                            {'apidoc': [...],
                             'applicationcontrol': [...],
                             },
                    'component': [...],
                    },
            'docutils': [...],
            }
        """
        
class IRegistrySearch(interface.Interface):
    """ Adapter interface that takes care of doing searches in
    different types of registry registrations.
    """
    
    def __init__(registration):
        """ Registers the registration in the adapter...
        """
        
    def searchRegistration(string, registry, caseSensitive):
        """ Implements the search...
            returns True or False
        """
        
    def getInterfaces():
        """ Returns a list with the interfaces involved in this registration
        """
        
    def getObject():
        """ Returns the registration
        """

class IViewInfo(interface.Interface):
    """The representation of an object that has views associated.
    """

    def getViews(layer=None):
        """Get the views for context object.

        Optional layer argument retrieves views registered for this layer.

        Returns iterator (view name, view factory) tuples.
        """

    def getAllViews():
        """Get all views for context objects, for any layer that is in a skin.

        Returns iterator of (skin name, (skin) layer, view name,
        view factory) tuples.

        The default layer will be returned with u'' as the skin name.
        """
        
class IObjectDescriptionProvider(interface.Interface):
    """Provide description objects for arbitrary objects.
    """
    def getDescription(obj_or_dotted_path, *args, **kw):
        """Get one description object for the object denoted by
        ``obj_or_dotted_path``.
        """
