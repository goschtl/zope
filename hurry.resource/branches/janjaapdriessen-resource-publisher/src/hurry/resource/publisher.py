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
    def __init__(self):
        self.directory_apps = {}
        for library in hurry.resource.libraries():
            app = FilterHiddenDirectoryApp(library.path)
            self.directory_apps[library.name] = app

    def __call__(self, environ, start_response):
        # When configured through Paste#urlmap, the WSGI environ['PATH_INFO']
        # does not contain the mapping URL segment any more.

        library_name = path_info_pop(environ)
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

        response = start_response

        next_segment = path_info_split(environ['PATH_INFO'])[0]
        if next_segment is not None and next_segment.startswith('hash:'):
            # Our hashed urls start with 'hash:'. Skip these URL segments.
            path_info_pop(environ)
            response = cache_header_start_response

        return directory_app(environ, response)


def make_publisher(global_conf):
    return Publisher()
