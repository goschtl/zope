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

$Id: servicecontainer.py,v 1.5 2003/09/02 20:46:50 jim Exp $
"""

from zope.component.exceptions import ComponentLookupError
from zope.app.interfaces.services.service import IPossibleSite, ISite
from zope.component.interfaces import IServiceService
from zope.app import zapi
import zope.interface

class ServiceManagerContainer:

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
        if ISite.isImplementedBy(self):
            raise TypeError("Already a site")

        if IServiceService.isImplementedBy(sm):
            self.__sm = sm
        else:
            raise ValueError('setSiteManager requires an IServiceService')

        zope.interface.directlyProvides(self, ISite)




from zope.app.event.function import Subscriber
from transaction import get_transaction
from zope.component.exceptions import ComponentLookupError

def fixup(event):
        database = event.database
        connection = database.open()
        app = connection.root().get('Application')
        if app is None:
            # No old data
            return
        fixfolder(app)
        get_transaction().commit()
        connection.close()

fixup = Subscriber(fixup)

def fixfolder(folder):
    if ISite.isImplementedBy(folder):
        # No need to do more, the conversion already happened!
        return
    try:
        sm = folder.getSiteManager()
    except ComponentLookupError:
        pass # nothing to do
    else:
        zope.interface.directlyProvides(folder, ISite)

    for item in folder.values():
        if IPossibleSite.isImplementedBy(item):
            fixfolder(item)
                
                
