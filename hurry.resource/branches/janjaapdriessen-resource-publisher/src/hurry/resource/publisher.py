import webob
from paste.request import path_info_pop, path_info_split
from paste.fileapp import DirectoryApp, CACHE_CONTROL, EXPIRES
from paste.httpexceptions import HTTPNotFound

import hurry.resource


class FilterHiddenDirectoryApp(DirectoryApp):
    def __call__(self, environ, start_response):
        path_info = environ['PATH_INFO']
        for segment in path_info.split('/'):
            if segment.startswith('.'):
                return HTTPNotFound()(environ, start_response)
        return DirectoryApp.__call__(self, environ, start_response)


class Publisher(object):
    def __init__(self, app, **local_conf):
        self._wrapped_app = app
        self.directory_apps = {}
        for library in hurry.resource.libraries():
            app = FilterHiddenDirectoryApp(library.path)
            self.directory_apps[library.name] = app

    def __call__(self, environ, start_response):
        path = environ['PATH_INFO']
        if hurry.resource.hash_signature not in path:
            # There's no hash signature found in the path, so we
            # cannot publish it from here. Leave the response to the
            # wrapped app.
            request = webob.Request(environ)
            response = request.get_response(self._wrapped_app)
            return response(environ, start_response)

        library_name = ''
        next_ = path_info_pop(environ)
        while next_:
            if next_.startswith(':%s:' % hurry.resource.hash_signature):
                # Skip over hash signature segment. The library name
                # will be that of the next step.
                library_name = path_info_pop(environ)
                break
            next_ = path_info_pop(environ)
            print 'STEPPIE', library_name, path, environ['PATH_INFO']

        try:
            directory_app = self.directory_apps[library_name]
        except KeyError:
            return HTTPNotFound()(environ, start_response)

        def cache_header_start_response(status, headers, exc_info=None):
            # Only set the cache control for succesful requests (200, 206).
            if status.startswith('20'):
                expires = CACHE_CONTROL.apply(
                    headers, max_age=10*CACHE_CONTROL.ONE_YEAR)
                EXPIRES.update(headers, delta=expires)
            return start_response(status, headers, exc_info)

        response = cache_header_start_response
        return directory_app(environ, response)

def make_publisher(app, global_conf, **local_conf):
    return Publisher(app, **local_conf)
