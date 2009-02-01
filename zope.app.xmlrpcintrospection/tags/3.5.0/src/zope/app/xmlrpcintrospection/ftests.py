##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Functional tests for xmlrpcintrospection

$Id$
"""

import re
import zope.interface
import zope.site.interfaces
import zope.publisher.interfaces.xmlrpc
from zope.testing import renormalizing
from zope.app.testing import ztapi, functional, setup
from zope.app.xmlrpcintrospection.testing import XmlrpcIntrospectionLayer

# FIXME: This should be a layer, but maybe people depend on it.
def setUp(test):
    setup.setUpTestAsModule(test, 'zope.app.xmlrpcintrospection.README')


def tearDown(test):
    # clean up the views we registered:

    # we use the fact that registering None unregisters whatever is
    # registered. We can't use an unregistration call because that
    # requires the object that was registered and we don't have that handy.
    # (OK, we could get it if we want. Maybe later.)

    ztapi.provideView(zope.site.interfaces.IFolder,
                        zope.publisher.interfaces.xmlrpc.IXMLRPCRequest,
                        zope.interface,
                        'contents',
                        None,
                        )
    ztapi.provideView(zope.site.interfaces.IFolder,
                        zope.publisher.interfaces.xmlrpc.IXMLRPCRequest,
                        zope.interface,
                        'contents',
                        None,
                        )

    setup.tearDownTestAsModule(test)


checker = renormalizing.RENormalizing([
    (re.compile(r"HTTP/1\.([01]) (\d\d\d) .*"), r"HTTP/1.\1 \2 <MESSAGE>"),
    ])


