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
"""

from zope.interface import directlyProvides
from zope.pipeline.interfaces import INoRequest
from zope.pipeline.interfaces import IPipelineApplicationList
from zope.pipeline.interfaces import IPipelineParticipant
from zope.pipeline.interfaces import IWSGIApplicationFactory


def create_pipeline(params, request_provides=None):
    """Return a pipeline as a WSGI application.

    The `params` contains a mapping of application name to
    factory keyword parameter map.  An example `params` would be
    ``{'open_root': {'database': zodb_db_object}}``.

    The `request_provides` parameter varies the pipeline according
    to the type of the `zope.request` in the WSGI environment.
    If the WSGI environment to process has no `zope.request`, the
    `request.provides` parameter should be None (the default).
    """
    if request_provides is None:
        request_provides = (INoRequest,)
    marker_request = MarkerRequest(request_provides)
    app_list = IPipelineApplicationList(marker_request)
    app = None
    for name in reversed(app_list.names):
        factory = IWSGIApplicationFactory(marker_request, name=name)
        app = factory.create(name, params, app)
        # If the app or some adapter needs to know the parameters
        # for the whole pipeline, tell it.
        participant = IPipelineParticipant(app, None)
        if participant is not None:
            participant.set_pipeline_params(app_name, params)
    return app


class MarkerRequest(object):
    """A marker object that claims to provide a request type.

    This is used for adapter lookup.
    """
    __slots__ = ('__provides__',)

    def __init__(self, request_type):
        directlyProvides(self, request_type)
