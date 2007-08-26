import transaction
import zope.interface
import zope.component
import zope.event

from zope.component import queryMultiAdapter
from zope.security.management import newInteraction, endInteraction
from zope.traversing.namespace import namespaceLookup
from zope.traversing.namespace import nsParse
from zope.traversing.interfaces import TraversalError
from zope.publisher.interfaces import IPublishTraverse, IPublication, NotFound
from zope.publisher.interfaces.browser import IBrowserPublisher, IBrowserRequest
from zope.location import LocationProxy

from zope.app.publisher.browser import queryDefaultViewName
from zope.app.publication.interfaces import IRequestPublicationFactory
from zope.app.publication.interfaces import BeforeTraverseEvent
from zope.app.publication.interfaces import EndRequestEvent
from zope.app.publication.zopepublication import Cleanup

import Acquisition
import ZPublisher.BaseRequest
from ZPublisher.mapply import mapply
from ZPublisher.BaseRequest import RequestContainer

from five.publication.request import BrowserRequest

class BrowserPublication(object):
    zope.interface.implements(IPublication)

    root_name = 'Application'

    def __init__(self, db):
        self.db = db

    def beforeTraversal(self, request):
        newInteraction(request)
        transaction.begin()

    def getApplication(self, request):
        # Open the database.
        conn = self.db.open()
        cleanup = Cleanup(conn.close)
        request.hold(cleanup)  # Close the connection on request.close()

        # Get the application object.
        root = conn.root()
        app = root.get(self.root_name, None)

        app = app.__of__(RequestContainer(REQUEST=request))
        request['PARENTS'].append(app)

        return app

    def callTraversalHooks(self, request, ob):
        zope.event.notify(BeforeTraverseEvent(ob, request))

    def traverseName(self, request, ob, name):
        bpth = getattr(object, '__before_publishing_traverse__', None)
        if bpth is not None:
            bpth(object, self)

        # mostly lifted from zope.app.publication.publicationtraverse
        lookup_name = name

        if name and name[:1] in '@+':
            # Process URI segment parameters.
            ns, lookup_name = nsParse(name)
            if ns:
                try:
                    subobject = namespaceLookup(ns, lookup_name, ob, request)
                except TraversalError:
                    raise NotFound(ob, name)

                return subobject

        if lookup_name == '.':
            return ob

        if IPublishTraverse.providedBy(ob):
            subobject = ob.publishTraverse(request, lookup_name)
        else:
            # self is marker
            adapter = queryMultiAdapter((ob, request), IPublishTraverse,
                                        default=self)
            if adapter is not self:
                subobject = adapter.publishTraverse(request, lookup_name)
            else:
                raise NotFound(ob, name, request)

        request['PARENTS'].append(subobject)
        return subobject

    def getDefaultTraversal(self, request, ob):
        if IBrowserPublisher.providedBy(ob):
            return ob.browserDefault(request)
        else:
            adapter = queryMultiAdapter((ob, request), IBrowserPublisher)
            if adapter is not None:
                ob, path = adapter.browserDefault(request)
                return ob, path
            else:
                return ob, None

    def afterTraversal(self, request, ob):
        pass #XXX

    def callObject(self, request, ob):
        def missing_name(name, context):
            if name == 'self':
                return ob
            #XXX what to do here?
            #raise TypeError('XXX')
        
        return mapply(ob, request.getPositionalArguments(), request,
                      missing_name=missing_name, context=request)

    def afterCall(self, request, ob):
        if request.method == 'HEAD':
            request.response.setResult('')

    def handleException(self, object, request, exc_info, retry_allowed=True):
        transaction.abort()
        # TODO handle Retry, ConflictError, etc.
        # TODO handle logging
        exception_type, exception, traceback = exc_info

        loc = object
        if Acquisition.aq_parent(object) is None:
            # Try to get an object, since we apparently have a method
            # Note: We are guaranteed that an object has a location,
            # so just getting the instance the method belongs to is
            # sufficient.
            loc = getattr(loc, 'im_self', loc)
            loc = getattr(loc, '__self__', loc)

        # Give the exception instance its location and look up the
        # view.
        exception = LocationProxy(exception, loc, '')
        name = queryDefaultViewName(exception, request)
        if name is not None:
            # TODO annotate the transaction 
            view = queryMultiAdapter((exception, request), name=name)
            if view is not None:
                # XXX should we use mapply here?
                body = self.callObject(request, view)
                request.response.setResult(body)
                transaction.commit()
            else:
                # This is the last resort. We shouldn't get here, but
                # in case we do, we have to set the result to something.
                request.response.setStatus(500)
                request.response.setResult('An error occurred.')

    def endRequest(self, request, ob):
        endInteraction()
        zope.event.notify(EndRequestEvent(ob, request))

class RequestPublicationFactory(object):
    zope.interface.implements(IRequestPublicationFactory)

    def canHandle(self, environment):
        return True

    def __call__(self):
        return BrowserRequest, BrowserPublication

class DefaultBrowserPublisher(ZPublisher.BaseRequest.DefaultPublishTraverse):
    zope.component.adapts(None, IBrowserRequest)
    zope.interface.implements(IBrowserPublisher)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def browserDefault(self, request):
        # Support for old __browser_default__
        if hasattr(self.context, '__browser_default__'):
            return self.context.__browser_default__(request)

        # If there's a default view name set and the view for this
        # default view exists, we'll use that.
        default_name = queryDefaultViewName(self.context, request)
        if (default_name is not None and
            queryMultiAdapter((self.context, request), name=default_name)
            is not None):
            # Adding '@@' here forces this to be a view.
            # A neater solution might be desireable.
            return self.context, ('@@' + default_name,)

        # Otherwise it's index_html...
        if getattr(self.context, 'index_html', None) is not None:
            return self.context, ('index_html',)

        # ... before __call__.
        return self.context, ()


    # XXX ZPublisher's DefaultPublishTraverse.publishTraverse seems to
    # do all the right things already.
    def XXXpublishTraverse(self, request, name):
        marker = object()
        subobj = getattr(self.context, name, marker)
        if subobj is not marker:
            return subobj

        view = queryMultiAdapter((self.context, request), name=name)
        if view is not None:
            return view

        raise NotFound(self.context, name)
