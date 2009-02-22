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
from zope.pipeline.envkeys import IMPLICIT_TRAVERSAL_STEPS_KEY
from zope.pipeline.envkeys import REQUEST_KEY
from zope.pipeline.envkeys import STRING_RESULT_HOOKS_KEY
from zope.publisher.interfaces import IWSGIApplication


class FixRelativeLinks(object):
    """WSGI middleware that fixes relative links.

    This application deals with request URLs that are problematic
    for relative links in HTML because the requested URL is too different
    from the traversed object's canonical URL.  It fixes the problem by
    either redirecting (before calling the app) or adding a base tag
    to the response text (after calling the app).
    """
    implements(IWSGIApplication)

    allow_redirect = True

    def __init__(self, next_app):
        self.next_app = next_app

    def __call__(self, environ, start_response):
        request = environ[REQUEST_KEY]

        need_fix = False
        allow_redirect = False

        if request.form_action:
            # When there is a :method or :action form variable, we need to
            # fix relative URLs, but not by redirecting.
            need_fix = True

        else:
            actual_steps = environ[IMPLICIT_TRAVERSAL_STEPS_KEY]

            # If the URL ends with a slash, the URL specified one
            # default traversal step, otherwise the URL specified zero.
            if environ['PATH_INFO'].endswith('/'):
                specified_steps = 1
            else:
                specified_steps = 0

            # Compare the number of default traversal steps specified
            # by the URL with the number of default traversal steps
            # actually performed. Set need_fix to True if the specified
            # number does not match the actual.
            if actual_steps != specified_steps:
                need_fix = True
                allow_redirect = (
                    self.allow_redirect and request.method == 'GET')

        if need_fix:
            if redirect:
                # Redirect, then end the pipeline early
                response = request.response
                response.redirect(request.getURL())
                start_response(
                    response.getStatusString(), response.getHeaders())
                return response.consumeBodyIter()

            # add a hook for altering string output.
            hooks = environ.setdefault(STRING_RESULT_HOOKS_KEY, [])
            hooks.append(self.string_result_hook)

        return self.next_app(environ, start_response)

    def string_result_hook(self, result, environ):
        # TODO: if result is HTML, add base tag and adjust the response
        # content-length.
        return result
