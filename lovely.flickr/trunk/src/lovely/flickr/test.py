##############################################################################
#
# Copyright (c) 2006 Lovely Systems and Contributors.
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
"""This module implements the flickr.test namespace

http://www.flickr.com/services/api/

$Id$
"""
__docformat__ = "reStructuredText"


import zope.interface
from zope.schema import fieldproperty
from lovely.flickr import interfaces, flickr, auth

class APITest(flickr.APIFlickr):
    """This class provides a pythonic interface to the ``flickr.test``
       namespace.
    """
    zope.interface.implements(interfaces.IAPITest)

    def echo(self, **kw):
        """See interfaces.IAPITest"""
        params = self.initParameters('flickr.test.echo', **kw)
        rsp = self.execute(params)
        return dict([(item.tag, item.text) for item in rsp.getchildren()])

    def login(self):
        """See interfaces.IAPITest"""
        params = self.initParameters('flickr.test.login')
        self.addAuthToken(params)
        self.sign(params)
        rsp = self.execute(params)
        user = rsp.find('user')
        return auth.User(unicode(user.get('id')),
                         unicode(user.find('username').text))

    def null(self):
        """See interfaces.IAPITest"""
        params = self.initParameters('flickr.test.null')
        self.addAuthToken(params)
        self.sign(params)
        self.execute(params)


def echo(api_key, **kw):
    __doc__ = interfaces.IAPITest['echo'].__doc__
    return APITest(api_key).echo(**kw)

def login(api_key, secret, auth_token):
    __doc__ = interfaces.IAPITest['login'].__doc__
    return APITest(api_key, secret, auth_token).login()

def null(api_key, secret, auth_token):
    __doc__ = interfaces.IAPITest['null'].__doc__
    return APITest(api_key, secret, auth_token).null()
