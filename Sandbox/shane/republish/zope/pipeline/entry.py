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

Use get_pipeline() to get a WSGI application built from a Zope pipeline.
"""

# _pipeline_cache: {(interfaces provided by the request) -> WSGI application}
_pipeline_cache = {}

def get_pipeline(request=None):
    if request is None:
        provided = (IUndecidedRequest,)
    else:
        provided = tuple(providedBy(request))
    pipeline = _pipeline_cache.get(provided)
    if pipeline is None:
        pipeline = make_pipeline(provided)
        _pipeline_cache[provided] = pipeline
    return pipeline

def make_pipeline(provided):
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
    return app

class MarkerRequest(object):
    """A marker object that claims to provide a request type.

    This is used for adapter lookup.
    """
    __slots__ = ('__provides__',)

    def __init__(self, request_type):
        directlyProvides(self, request_type)
