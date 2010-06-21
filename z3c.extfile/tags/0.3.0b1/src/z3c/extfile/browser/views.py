from z3c.filetype import api
from z3c.filetype.interfaces import filetypes
from zope import interface
from zope.cachedescriptors.property import Lazy
import zope.datetime
from zope.publisher.browser import BrowserView
from zope.traversing.browser import absoluteurl
from zope.app.component import hooks

class ReadFileAbsoluteURL(absoluteurl.SiteAbsoluteURL):

    def __str__(self):
        siteURL = absoluteurl.absoluteURL(hooks.getSite(), self.request)
        return '%s/++static++%s' % (siteURL, self.context.digest)

    __call__ = __str__

class ReadFileView(BrowserView):

    @Lazy
    def contentType(self):
        ifaces = api.getInterfacesFor(self.context)
        decl = interface.Declaration(ifaces)
        for iface in decl.flattened():
            mt = iface.queryTaggedValue(filetypes.MT)
            if mt is not None:
                return mt
        raise ValueError, "Unable to detect content type %r" % self.context

    def __call__(self):
        """Sets various headers if the request for IFLVFile."""

        self.request.response.setHeader('Content-Type',
                                        self.contentType)
        self.request.response.setHeader('Content-Length',
                                        len(self.context))
        ms= self.request.getHeader('If-Modified-Since', None)
        if ms is not None:
            # we cannot be modified, so we can return a 304 anytime
            self.request.response.setStatus(304)
            return ''
        # set the modified header to creation time
        self.request.response.setHeader(
            'Last-Modified',
            zope.datetime.rfc1123_date(self.context.ctime))
        # let it cache forever (360 days)
        self.request.response.setHeader(
            'Cache-Control',
            's-max-age=31104000; max-age=31104000')
        return self.context

