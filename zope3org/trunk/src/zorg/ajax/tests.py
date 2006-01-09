##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""

$Id: tests.py 39651 2005-10-26 18:36:17Z oestermeier $
"""

import unittest
import zope

from zope.testing import doctest
from zope.app.testing.setup import placefulSetUp, placefulTearDown
from zope.app.session.session import ClientId, Session
from zope.app.session.session import PersistentSessionDataContainer
from zope.publisher.interfaces import IRequest
from zope.app.session.http import CookieClientIdManager
from zope.app.session.interfaces import ISessionDataContainer
from zope.app.session.interfaces import IClientId
from zope.app.session.interfaces import IClientIdManager, ISession

from zope.app.folder import rootFolder
from zope.app.folder import Folder
from zope.app.file import File

from zope.publisher.browser import TestRequest

def sessionSetUp(test=None) :
    """
        >>> request = TestRequest()
        >>> ISession(request)   #doctest: +ELLIPSIS
        <zope.app.session.session.Session object at ...>
    """
    
    zope.interface.classImplements(TestRequest, IRequest)
    
    zope.component.provideAdapter(ClientId, [IRequest], IClientId, )
    zope.component.provideAdapter(Session, [IRequest], ISession)
    zope.component.provideUtility(CookieClientIdManager(), IClientIdManager)
    sdc = PersistentSessionDataContainer()
    zope.component.provideUtility(sdc, ISessionDataContainer, 'zorg.ajax')


def ajaxSetUp(test) :
    placefulSetUp()
    sessionSetUp(test)
    
def ajaxTearDown(test) :
    placefulTearDown()
 


def test_suite():

 
    flags=doctest.NORMALIZE_WHITESPACE+doctest.ELLIPSIS
                    
    return unittest.TestSuite((
        doctest.DocTestSuite(setUp=ajaxSetUp, tearDown=ajaxTearDown),
        doctest.DocTestSuite('zorg.ajax.page', setUp=ajaxSetUp, 
                                               tearDown=ajaxTearDown,
                                               optionflags=flags),
        doctest.DocTestSuite('zorg.ajax.livepage', setUp=ajaxSetUp, 
                                               tearDown=ajaxTearDown,
                                               optionflags=flags),                                       
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
        

