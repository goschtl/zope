##############################################################################
#
# Copyright (c) Zope Corporation and Contributors.
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

import pkg_resources
import webob


class Application:

    def __init__(self, publication):
        self.publication = publication

    def __call__(self, environ, start_response):
        handle_errors = environ.get('wsgi.handleErrors', True)
        request = webob.Request(environ)
        publication = self.publication
        request.publication = publication
        request.response = webob.Response()
        response.request = request

        try:
            publication.beforeTraversal(request)

            obj = publication.getObject(request)
            publication.afterTraversal(request, obj)

            result = publication.callObject(request, obj)
            if result is not request.response:
                response.setResult(result)

            publication.afterCall(request, obj)

        except:
            try:
                publication.handleException(
                    obj, request, sys.exc_info(), True)
            except:
                # bad exception handler.
                if handle_errors:
                    self.internalError(request.response)
                else:
                    raise

            if not handle_errors:
                raise

        finally:
            publication.endRequest(request, obj)

        return request.response(environ, start_response)

    def internalError(self, response):
        response.status = 500
        response.body = "A system error occurred."


class PasteApplication(Application):

    def __init__(self, global_config, publication_name, **options):
        if not publication_name.startswith('egg:'):
            raise ValueError(
                'Invalid publication: .\n'
                'The publication specification must start with "egg:".\n'
                'The publication must name a publication entry point.'
                % publication_name)

        pub_class = get_egg(publication_name[4:],
                            'zope.publisher.publication_factory')
        self.publication = pub_class(global_config, **options)

def get_egg(name, group):
    if '#' in name:
        egg, entry_point = name.split('#', 1)
    else:
        egg, entry_point = name, 'default'

    return pkg_resources.load_entry_point(egg, group, entry_point)
