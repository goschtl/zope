##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
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
from zope import component
from zope.app.appsetup.bootstrap import ensureUtility, getInformationFromEvent
from zope.processlifetime import IDatabaseOpenedWithRoot
from zope.principalannotation.utility import PrincipalAnnotationUtility
from zope.principalannotation.interfaces import IPrincipalAnnotationUtility


@component.adapter(IDatabaseOpenedWithRoot)
def bootStrapSubscriber(event):
    """ Create utility at that time if not yet present """

    db, connection, root, root_folder = getInformationFromEvent(event)

    ensureUtility(root_folder, IPrincipalAnnotationUtility,
                  'PrincipalAnnotation', PrincipalAnnotationUtility)

    transaction.commit()
    connection.close()
