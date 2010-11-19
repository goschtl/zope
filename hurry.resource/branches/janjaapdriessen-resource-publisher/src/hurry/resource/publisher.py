from itertools import dropwhile

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
    def __init__(self, app):
        self._wrapped_app = app
        self.directory_apps = {}
        for library in hurry.resource.libraries():
            app = FilterHiddenDirectoryApp(library.path)
            self.directory_apps[library.name] = app

    def __call__(self, environ, start_response):
        path_info = environ['PATH_INFO']

        path_segments = [s for s in path_info.split('/') if s.strip() != '']

        def hash_find(segment):
            return not segment.startswith(hurry.resource.publisher_signature)

        new_path = list(dropwhile(hash_find, path_segments))

        if len(new_path) == 0:
            # There's no hash signature found in the path, so we
            # cannot publish it from here. Leave the response to the
            # wrapped app.
            return self._wrapped_app(environ, start_response)

        try:
            hash = new_path.pop(0)
            library_name = new_path.pop(0)
        except IndexError:
            return HTTPNotFound()(environ, start_response)

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

        # Reconstruct information for the directory_app to work with.
        environ['PATH_INFO'] = '/' + '/'.join(new_path)
        return directory_app(environ, cache_header_start_response)

def make_publisher(app, global_conf):
    return Publisher(app, **local_conf)
