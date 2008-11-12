from zope import interface
from zope import component

from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.interfaces.browser import IBrowserPublisher
from zope.publisher.browser import TestRequest
from zope.app.publisher.browser.resource import Resource
from zope.publisher.interfaces import NotFound
from zope.datetime import rfc1123_date
from zope.datetime import time as timeFromDateTimeString

from interfaces import IResourceCollector
from interfaces import IResourceManager

import mimetypes
import tempfile
import sha
import time

class TemporaryResource(Resource):
    interface.implements(IBrowserPublisher)

    def __init__(self, request, f, content_type, lmt):
        self.request = request
        self.__file = f
        self.content_type = content_type
        self.lmt = lmt
        self.context = self

    def publishTraverse(self, request, name):
        '''See interface IBrowserPublisher'''
        raise NotFound(None, name)

    def browserDefault(self, request):
        '''See interface IBrowserPublisher'''
        return getattr(self, request.method), ()

    def GET(self):
        lmt = self.lmt

        request = self.request
        response = request.response

        # HTTP If-Modified-Since header handling. This is duplicated
        # from OFS.Image.Image - it really should be consolidated
        # somewhere...
        header = request.getHeader('If-Modified-Since', None)
        if header is not None:
            header = header.split(';')[0]
            # Some proxies seem to send invalid date strings for this
            # header. If the date string is not valid, we ignore it
            # rather than raise an error to be generally consistent
            # with common servers such as Apache (which can usually
            # understand the screwy date string as a lucky side effect
            # of the way they parse it).
            try:    mod_since=long(timeFromDateTimeString(header))
            except: mod_since=None
            if mod_since is not None:
                last_mod = long(lmt)
                if last_mod > 0 and last_mod <= mod_since:
                    response.setStatus(304)
                    return ''

        # set response headers
        response.setHeader('Content-Type', self.content_type)
        response.setHeader('Last-Modified', rfc1123_date(lmt))

        secs = 31536000 # one year - never expire
        t = time.time() + secs
        response.setHeader('Cache-Control', 'public,max-age=%s' % secs)
        response.setHeader(
            'Expires', time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(t)))

        f = self.__file
        f.seek(0)
        return f.read()

class TemporaryResourceFactory(object):
    def __init__(self, f, checker, content_type, name):
        self.__file = f
        self.__name = name
        self.__checker = checker
        self.content_type = content_type
        self.lmt = time.time()

    def __call__(self, request):
        resource = TemporaryResource(request, self.__file, self.content_type, self.lmt)
        resource.__Security_checker__ = self.__checker
        resource.__name__ = self.__name
        return resource

class TemporaryRequest(TestRequest):
    def __init__(self, request):
        self.__request = request
        TestRequest.__init__(self)

    def getURL(self, *args, **kwargs):
        return self.__request.getURL(*args, **kwargs)

    def getApplicationURL(self, *args, **kwargs):
        return self.__request.getApplicationURL(*args, **kwargs)

    def getVirtualHostRoot(self):
        return self.__request.getVirtualHostRoot()

class ResourceCollector(object):
    interface.implements(IResourceCollector)
    component.adapts(IBrowserRequest)

    def __init__(self, request):
        self.request = request

    def collect(self):
        resources = []
        names = []

        request = self._get_request()

        for name, manager in self._get_managers():
            items = manager.getResources(request)

            # filter out duplicates
            rs = [resource for name, resource in items if name not in names]
            names.extend((name for name, resource in items))

            # sort
            self.sort(rs)

            # merge
            self.merge(rs)

            resources.extend(rs)

        return tuple(resources)

    def sort(self, resources):
        resources.sort(key=lambda resource: resource.context.content_type)

    def merge(self, resources):
        pass

    def _get_request(self):
        return TemporaryRequest(self.request)

    def _get_managers(self):
        managers = [(name, manager) for name, manager in \
                    component.getAdapters((self.request,), IResourceManager) if \
                    manager.available()]

        managers.sort(key=lambda (name, manager): name)

        return managers

class DigestResourceCollector(ResourceCollector):

    def _build_factory(f, resource, content_type, name):
        # adopt last resource's security checker
        checker = resource.__Security_checker__

        return TemporaryResourceFactory(f, checker, content_type, name)

    def merge(self, resources):
        by_type = {}
        for resource in resources:
            by_type.setdefault(resource.context.content_type, []).append(resource)

        del resources[:]
        merged = resources

        for content_type, resources in by_type.items():
            f = tempfile.TemporaryFile()

            for resource in resources:
                method, views = resource.browserDefault(self.request)

                print >> f, "/* %s */" % resource.__name__
                f.write(method())
                print >> f, ""

            # generate filename
            ext = mimetypes.guess_extension(content_type)
            f.seek(0)
            digest = sha.new(f.read()).hexdigest()
            name = digest + ext

            # check if resource is already registered
            res = component.queryAdapter((self.request,), name=name)

            if res is None:
                factory = self._build_factory(
                    f, resource, content_type, name)

                # register factory
                component.provideAdapter(
                    factory, (IBrowserRequest,), interface.Interface, name=name)

                res = factory(self.request)

            merged.append(res)
