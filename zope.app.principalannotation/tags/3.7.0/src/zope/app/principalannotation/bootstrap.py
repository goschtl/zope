##############################################################################
#
# Copyright (c) 2009 Zope Corporation and Contributors.
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
"""Bootstrap code for principal annotation utility.

$Id$
"""

import transaction

from zope.app.appsetup.bootstrap import ensureUtility, getInformationFromEvent

from zope.principalannotation.utility import PrincipalAnnotationUtility
from zope.principalannotation.interfaces import IPrincipalAnnotationUtility

def bootStrapSubscriber(event):
    """Subscriber to the IDatabaseOpenedWithRootEvent

    Create utility at that time if not yet present
    """

    db, connection, root, root_folder = getInformationFromEvent(event)

    ensureUtility(root_folder, IPrincipalAnnotationUtility,
                  'PrincipalAnnotation', PrincipalAnnotationUtility)

    transaction.commit()
    connection.close()
