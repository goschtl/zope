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
"""Interfaces for the zope.app.process package.

$Id$
"""

from zope.interface import Interface


class IPublicationRequestFactoryFactory(Interface):
    """Publication request factory factory"""

    def realize(db):
        """Create a publication and request factory for a given database

        Return a IPublicationRequestFactory for the given database.
        """


class IPublicationRequestFactory(Interface):
    """Publication request factory"""

    def __call__(input_stream, output_steam, env):
        """Create a request object to handle the given inputs

        A request is created and configured with a publication object.
        """


class IRequestFactory(IPublicationRequestFactory,
                      IPublicationRequestFactoryFactory):
    """This is a pure read-only interface, since the values are set through
       a ZCML directive and we shouldn't be able to change them.
    """


class ISimpleRegistry(Interface):
    """
    The Simple Registry is minimal collection of registered objects. This can
    be useful, when it is expected that objects of a particular type are added
    from many places in the system (through 3rd party products for example).

    A good example for this are the Formulator fields. While the basic types
    are defined inside the Formulator tree, other parties might add many
    more later on in their products, so it is useful to provide a registry via
    ZCML that allows to collect these items.

    There is only one constraint on the objects. They all must implement a
    particular interface specified during the initialization of the registry.

    Note that it does not matter whether we have classes or instances as
    objects. If the objects are instances, they must implement simply
    IInstanceFactory.
    """

    def register(name, object):
        """Registers the object under the id name."""

    def getF(name):
        """This returns the object with id name."""
