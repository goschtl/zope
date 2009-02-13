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
"""The main entry point for the zope.pipeline package.

Use get_database_pipeline() or get_pipeline() to get a WSGI
application built from a pipeline.
"""

from zope.component import getMultiAdapter
from zope.interface import directlyProvides
from zope.interface import providedBy
from zope.pipeline.interfaces import IPipelineApplicationList
from zope.pipeline.interfaces import IUndecidedRequest
from zope.publisher import IWSGIApplication
from zope.testing import cleanup

# _pipeline_cache: {(interfaces provided by the request) -> WSGI application}
_pipeline_cache = {}
cleanup.addCleanUp(_pipeline_cache.clear)

def get_database_pipeline(database, global_environ=None):
    if global_environ is None:
        global_environ = {}
    global_environ['zope.database'] = database
    return get_pipeline(global_environ=global_environ)

def get_pipeline(request=None, global_environ=None):
    if request is None:
        provided = (IUndecidedRequest,)
    else:
        provided = tuple(providedBy(request))
    pipeline = _pipeline_cache.get(provided)
    if pipeline is None:
        pipeline = make_pipeline(provided, global_environ)
        _pipeline_cache[provided] = pipeline
    return pipeline

def make_pipeline(provided, global_environ=None):
    marker_req = MarkerRequest(provided)
    app_list = IPipelineApplicationList(marker_req)
    names = list(app_list.names)  # make a copy
    # The last name in the list is an application.
    name = names.pop()
    app = IWSGIApplication(marker_req, name=name)
    while names:
        # The rest of the names are middleware.
        name = names.pop()
        app = getMultiAdapter(
            (app, marker_req), IWSGIApplication, name=name)
    if global_environ:
        # augment the WSGI environment with some data
        def add_global_environ(environ, start_response):
            environ.update(global_environ)
            return inner_app(environ, start_response)
        directlyProvides(add_global_environ, IWSGIApplication)
        return add_global_environ
    else:
        return app

class MarkerRequest(object):
    """A marker object that claims to provide a request type.

    This is used for adapter lookup.
    """
    __slots__ = ('__provides__',)

    def __init__(self, request_type):
        directlyProvides(self, request_type)
