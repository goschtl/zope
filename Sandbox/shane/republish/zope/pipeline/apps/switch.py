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


from zope.interface import implements
from zope.publisher.interfaces import IWSGIApplication

from zope.pipeline.entry import get_pipeline

class SwitchPipeline(object):
    """WSGI application that switches to a pipeline based on the request type.

    Requires 'zope.request' in the environment.
    """
    implements(IWSGIApplication)

    def __call__(self, environ, start_response):
        request = environ['zope.request']
        app = get_pipeline(request)
        return app(environ, start_response)

    def __repr__(self):
        return '%s()' % self.__class__.__name__
