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
"""
$Id: IZopeContainer.py,v 1.4 2002/12/12 11:32:29 mgedmin Exp $
"""

import IContainer

class IZopeItemContainer(IContainer.IItemContainer):

    def __getitem__(key):
        """Return the content for the given key

        Raises KeyError if the content can't be found.

        The returned value will be in the context of the container.
        """



class IZopeSimpleReadContainer(IZopeItemContainer,
                               IContainer.ISimpleReadContainer):
    """Readable content containers
    """

    def get(key, default=None):
        """Get a value for a key

        The default is returned if there is no value for the key.

        The value for the key will be in the context of the container.
        """



class IZopeReadContainer(IZopeSimpleReadContainer, IContainer.IReadContainer):
    """Readable containers that can be enumerated.
    """


    def values():
        """Return the values of the mapping object in the context of
           the container
        """

    def items():
        """Return the items of the mapping object in the context
           of the container
        """



class IZopeWriteContainer(IContainer.IWriteContainer):
    """An interface for the write aspects of a container."""

    def setObject(key, object):
        """Add the given object to the container under the given key.

        Raises a ValueError if key is an empty string, unless the
        context wrapper chooses a different key.

        Returns the key used, which might be different than the given key.

        If the object has an adpter to IAddNotifiable then the manageAfterAdd
        method on the adpter will be called after the object is added.

        An IObjectAddedEvent will be published after the object is added and
        after manageAfterAdd is called. The event object will be the added
        object in the context of the container

        An IObjectModifiedEvent will be published after the IObjectAddedEvent
        is published. The event object will be the container.
        """

    def __delitem__(key):
        """Delete the keyd object from the context of the container.

        Raises a KeyError if the object is not found.

        If the object has an adpter to IDeleteNotifiable then the
        manageBeforeDeleteObject method on the adpter will be called before
        the object is removed.

        An IObjectRemovedEvent will be published before the object is
        removed and before  manageBeforeDeleteObject is called.
        The event object will be the removed from the context of the container

        An IObjectModifiedEvent will be published after the IObjectRemovedEvent
        is published. The event object will be the container.
        """

class IZopeContainer(IZopeReadContainer, IZopeWriteContainer, IContainer.IContainer):
    """Readable and writable content container."""

