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
"""ServiceManagerContainer implementation.

$Id: servicecontainer.py,v 1.9 2004/03/05 22:09:16 jim Exp $
"""

import zope.interface

from transaction import get_transaction
from zope.app.container.contained import Contained
from zope.app.event.function import Subscriber
from zope.app import zapi
from zope.app.interfaces.services.service import IPossibleSite, ISite
from zope.component.exceptions import ComponentLookupError
from zope.component.interfaces import IServiceService
from zope.interface import implements

class ServiceManagerContainer(Contained):

    """Implement access to the service manager (++etc++site).

    This is a mix-in that implements the IPossibleSite
    interface; for example, it is used by the Folder implementation.
    """

    zope.interface.implements(IPossibleSite)

    __sm = None

    def getSiteManager(self):
        if self.__sm is not None:
            return self.__sm
        else:
            raise ComponentLookupError('no site manager defined')

    def setSiteManager(self, sm):
        if ISite.providedBy(self):
            raise TypeError("Already a site")

        if IServiceService.providedBy(sm):
            self.__sm = sm
            sm.__name__ = '++etc++site'
            sm.__parent__ = self
        else:
            raise ValueError('setSiteManager requires an IServiceService')

        zope.interface.directlyProvides(
            self,
            ISite,
            zope.interface.directlyProvidedBy(self))

def fixup(event):
        database = event.database
        connection = database.open()
        app = connection.root().get('Application')
        if app is None or ISite.providedBy(app):
            # No old data
            return
        print "Fixing up sites that don't implement ISite"
        fixfolder(app)
        get_transaction().commit()
        connection.close()

fixup = Subscriber(fixup)

def fixfolder(folder):
    if ISite.providedBy(folder):
        # No need to do more, the conversion already happened!
        return
    try:
        folder.getSiteManager()
    except ComponentLookupError:
        pass # nothing to do
    else:
        zope.interface.directlyProvides(
            folder,
            ISite,
            zope.interface.directlyProvidedBy(folder),
            )

    for item in folder.values():
        if IPossibleSite.providedBy(item):
            fixfolder(item)
