##############################################################################
#
# Copyright (c) 2009 Fabio Tranchitella <fabio@tranchitella.it>
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
$Id$
"""

from zope.dottedname.resolve import resolve


class ProxyMiddleware(object):
    """WSGI application filter to add support for object proxy"""

    def __init__(self, app, proxy):
        self.app = app
        if isinstance(proxy, str):
            proxy = resolve(proxy)
        self.proxy = proxy

    def __call__(self, environ, start_response):
        environ['bobopublisher.proxy'] = self.proxy
        return self.app(environ, start_response)


def make_proxy_middleware(app, global_conf, proxy):
    """Configure a ProxyMiddleware middleware"""
    return ProxyMiddleware(app, proxy)
