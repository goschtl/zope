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
"""interfaces for shortcut package

$Id$
"""
from zope import interface, schema
import zope.app.container.interfaces
import zope.component.interfaces

from zc.shortcut.i18n import _

REPOSITORY_NAME = "shortcutTargetRepository"
NEXT_URL_NAME = "nextURL"

class IShortcut(interface.Interface):

    target = interface.Attribute('ITargetProxy of the referred-to object.')
    raw_target = interface.Attribute(
        'the referred-to object without the ITargetProxy wrapper')

class ITraversalProxy(interface.Interface):
    __traversed_parent__ = interface.Attribute(
        "Traversed parent of the proxied object.")

    __traversed_name__ = schema.TextLine(
        title=_("Shortcut name"),
        description=_("Name used to traverse to the proxied object from the "
                      "traversal parent"),
        required=False,
        default=None,
        )

class ITargetProxy(ITraversalProxy):
    """Proxy to an object provided by a shortcut.

    This proxy provides some additional information based on the shortcut.
    """

    __shortcut__ = interface.Attribute(
        "The shortcut for which the proxied object was the target")


class ITraversedURL(interface.Interface):
    def __str__():
        """Return a utf-8 encoded string of the traversed URL.
        
        appropriate values are escaped."""

    def __unicode__():
        """return unicode of the traversed URL.
        
        values are not escaped"""

class IShortcutPackage(interface.Interface):
    def traversedURL(ob, request):
        """return an ITraversedURL for the ob and request"""

class IAdding(zope.app.container.interfaces.IAdding):
    """traversal-aware and enhanced IAdding"""

    def action(type_name='', id=''):
        """The same as zope.app's IAdding's action method, except that
        redirects use traversedURL instead of absoluteURL."""
    
    def nextURL():
        """tries to get a nextURL by getting a named adapter (the value in the
        NEXT_URL_NAME constant above) for the adding, the newly added content
        (adding.context[adding.contentName]), and the container 
        (adding.context).  If a nextURL is returned, use it; otherwise, return
        the traversedURL of the container + "/@@contents.html". """

class IObjectLinker(interface.Interface):

    def linkTo(target, new_name=None):
        """Make a shortcut to this object in the `target` given.

        Returns the new name of the shortcut within the `target`.
        After the new shortcut is made, publish an IObjectCreated event for
        the new shortcut.
        """

    def linkable():
        """Returns ``True`` if the object is linkable, otherwise ``False``."""

    def linkableTo(target, name=None):
        """Say whether the object can be linked to the given `target`.

        Returns ``True`` if it can be linked there. Otherwise, returns
        ``False``.
        """

class IShortcutTypePrecondition(zope.interface.Interface):

    def __call__(container, name, object):
        """Test whether container setitem arguments are valid.

        Raise zope.interface.Invalid if the objet is invalid.
        """

    def factory(container, name, factory):
        """Test whether objects provided by the factory are acceptable

        Return a boolean value.
        """

class IShortcutFactory(zope.component.interfaces.IFactory):
    """factory that creats in a repository and returns a shortcut
    
    getInterfaces should always return IShortcut.
    """

    def getTargetInterfaces():
        "return interfaces that the target will implement"
