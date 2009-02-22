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
from zope.interface import providedBy
from zope.publisher.interfaces import IWSGIApplication

from zope.pipeline.entry import create_pipeline
from zope.pipeline.envkeys import REQUEST_KEY
from zope.pipeline.interfaces import IPipelineParticipant


class SwitchPipeline(object):
    """WSGI application that switches to a pipeline based on the request type.

    This should be placed at the end of the INoRequest pipeline.
    Requires 'zope.pipeline.request' in the environment.
    """
    implements(IWSGIApplication, IPipelineParticipant)

    def __init__(self):
        # _cache: {(interfaces provided by the request) -> pipeline}
        self._cache = {}

    def set_pipeline_params(self, name, pipeline_params):
        self.pipeline_params = pipeline_params

    def __call__(self, environ, start_response):
        request = environ[REQUEST_KEY]
        provided = tuple(providedBy(request))
        pipeline = self._cache.get(provided)
        if pipeline is None:
            pipeline = create_pipeline(self.pipeline_params, provided)
            self._cache[provided] = pipeline
        return pipeline(environ, start_response)

    def __repr__(self):
        return '%s()' % self.__class__.__name__
