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

from ZODB.POSException import ConflictError
from zope.publisher.interfaces.exceptions import Retry

from zope.pipeline.autotemp import AutoTemporaryFile
from zope.pipeline.envkeys import CAN_RETRY_KEY


class RetryApp(object):
    """Retries requests when a Retry or ConflictError propagates.

    This app should enclose the app that creates zope.pipeline.request.
    It sets an environment variable named 'zope.pipeline.can_retry'.
    The 'handle_error' app should propagate Retry or ConflictError
    when 'zope.pipeline.can_retry' is true.
    """

    def __init__(self, next_app, retry_errors=(ConflictError, Retry),
            max_attempts=3):
        self.next_app = next_app
        self.retry_errors = retry_errors
        self.max_attempts = max_attempts

    def __call__(self, environ, start_response):
        wsgi_input = environ.get('wsgi.input')
        if wsgi_input is not None:
            try:
                wsgi_input.seek(0)
            except (AttributeError, IOError):
                # make the input stream rewindable
                f = AutoTemporaryFile()
                f.copyfrom(wsgi_input)
                f.seek(0)
                wsgi_input = f

        def retryable_start_response(status, response_headers, exc_info=None):
            start_response_params[:] = [status, response_headers, exc_info]
            tmp = AutoTemporaryFile()
            output_file[:] = [tmp]
            return tmp

        attempt = 1
        while attempt < self.max_attempts:
            start_response_params = []
            output_file = []
            env_copy = environ.copy()
            env_copy['wsgi.input'] = wsgi_input
            env_copy[CAN_RETRY_KEY] = True
            try:
                res = self.next_app(env_copy, retryable_start_response)
            except self.retry_errors:
                if wsgi_input is not None:
                    wsgi_input.seek(0)
                attempt += 1
            else:
                if start_response_params:
                    dest = start_response(*tuple(start_response_params))
                    src = output_file[0]
                    src.seek(0)
                    src.copyto(dest)
                    src.close()
                return res

        # try once more, this time without retry support
        return self.next_app(environ, start_response)
