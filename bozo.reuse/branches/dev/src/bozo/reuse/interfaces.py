##############################################################################
#
# Copyright Zope Foundation and Contributors.
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

import bobo
import zope.interface
import zope.publisher.interfaces.browser

class IResource(zope.interface.Interface):

    def bobo_response(request, path, method):
        """Return a response for the given request, path and method

        The response is a callable with the same signature as a WSGI
        application.
        """

# XXX bobo should expose somethinbg we can use:
zope.interface.classImplements(bobo._Handler, IResource)

class IRequest(zope.publisher.interfaces.browser.IBrowserRequest):
    """Browser requests that also provide the webob.Request API
    """
