##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
# 
##############################################################################
import sys
from types import StringType, ClassType
from zLOG import LOG, ERROR, INFO

from ZODB.POSException import ConflictError

from Zope.Publisher.DefaultPublication import DefaultPublication
from Zope.Publisher.mapply import mapply
from Zope.Publisher.Exceptions import Retry

from Zope.Security.SecurityManagement import getSecurityManager
from Zope.Security.SecurityManagement import newSecurityManager
from Zope.Security.Checker import ProxyFactory

from Zope.Proxy.ProxyIntrospection import removeAllProxies

from Zope.App.ComponentArchitecture.IServiceManagerContainer \
     import IServiceManagerContainer

from Zope.Exceptions import Unauthorized

from Zope.App.Security.Registries.PrincipalRegistry \
     import principalRegistry as prin_reg

from Zope.App.Security.IUnauthenticatedPrincipal \
     import IUnauthenticatedPrincipal

from Zope.App.OFS.Content.Folder.RootFolder import RootFolder

from PublicationTraverse import PublicationTraverse

from Zope.Proxy.ContextWrapper import ContextWrapper

# XXX Should this be imported here?
from Transaction import get_transaction

class RequestContainer:
    # TODO: add security assertion declaring access to REQUEST

    def __init__(self, request):
        self.REQUEST = request


class Cleanup:
    def __init__(self, f):
        self.__del__ = f


class ZopePublication(object, PublicationTraverse, DefaultPublication):
    """Base Zope publication specification."""

    version_cookie = 'Zope-Version'
    root_name = 'Application'

    def __init__(self, db):
        # db is a ZODB.DB.DB object.
        self.db = db

    def beforeTraversal(self, request):

        # Try to authenticate against the default global registry.
        id = prin_reg.authenticate(request)
        if id is None:
            id = prin_reg.unauthenticatedPrincipal()
            if id is None:
                raise Unauthorized # If there's no default principal

        newSecurityManager(id)
        request.user = prin_reg.getPrincipal(id)
        get_transaction().begin()

    def _maybePlacefullyAuthenticate(self, request, ob):
        if not IUnauthenticatedPrincipal.isImplementedBy(request.user):
            # We've already got an authenticated user. There's nothing to do.
            # Note that beforeTraversal guarentees that user is not None.
            return

        if not IServiceManagerContainer.isImplementedBy(ob):
            # We won't find an authentication service here, so give up.
            return

        sm = removeAllProxies(ob).queryServiceManager()
        if sm is None:
            # No service manager here, and thus no auth service
            return

        sm = ContextWrapper(sm, ob, name="++etc++Services")
        
        auth_service = sm.get('Authentication')
        if auth_service is None:
            # No auth service here
            return

        # Try to authenticate against the auth service
        id = auth_service.authenticate(request)
        if id is None:
            id = auth_service.unauthenticatedPrincipal()
            if id is None:
                # nothing to do here
                return

        newSecurityManager(id)
        request.user = auth_service.getPrincipal(id)
        

    def callTraversalHooks(self, request, ob):
        # Call __before_publishing_traverse__ hooks

        # This is also a handy place to try and authenticate.
        self._maybePlacefullyAuthenticate(request, ob)

    def afterTraversal(self, request, ob):
        #recordMetaData(object, request)
        self._maybePlacefullyAuthenticate(request, ob)
            

    def openedConnection(self, conn):
        # Hook for auto-refresh
        pass

    def getApplication(self, request):

        # If the first name is '++etc++ApplicationControl', then we should
        # get it rather than look in the database!
        stack = request.getTraversalStack()
        if stack:
            name = stack[-1]
            if name == '++etc++ApplicationController':
                stack.pop() # consume the name
                request.setTraversalStack(stack) # Reset the stack
                return self.traverseName(request, None, name)
        
        # Open the database.
        version = request.get(self.version_cookie, '')
        conn = self.db.open(version)

        cleanup = Cleanup(conn.close)
        request.hold(cleanup)  # Close the connection on request.close()

        self.openedConnection(conn)
##        conn.setDebugInfo(getattr(request, 'environ', None), request.other)

        root = conn.root()
        app = root.get(self.root_name, None)
        
        if app is None:
            raise SystemError, "Zope Application Not Found"

        return ProxyFactory(app)

    def getDefaultTraversal(self, request, ob):
        return ob, None

    def callObject(self, request, ob):
        return mapply(ob, request.getPositionalArguments(), request)

    def afterCall(self, request):
        get_transaction().commit()

    def handleException(self, request, exc_info, retry_allowed=1):
        try:
            # Abort the transaction.
            get_transaction().abort()

            # Delegate Unauthorized errors to the authentication service
            # XXX Is this the right way to handle Unauthorized?  We need
            # to understand this better.
            if isinstance(exc_info[1], Unauthorized):
                sm = getSecurityManager()
                id = sm.getPrincipal()
                prin_reg.unauthorized(id, request) # May issue challenge
                request.response.handleException(exc_info)
                return


            # XXX This is wrong. Should use getRequstView:
            # 
            # 
            # # Look for a component to handle the exception.
            # traversed = request.traversed
            # if traversed:
            #     context = traversed[-1]
            #     #handler = getExceptionHandler(context, t, IBrowserPublisher)
            #     handler = None  # no getExceptionHandler() exists yet.
            #     if handler is not None:
            #         handler(request, exc_info)
            #         return

            # Convert ConflictErrors to Retry exceptions.
            if retry_allowed and isinstance(exc_info[1], ConflictError):
                LOG('Zope Publication', INFO,
                    'Competing writes/reads at %s'
                    % request.get('PATH_INFO', '???'),
                    error=sys.exc_info())
                raise Retry

            # Let the response handle it as best it can.
            # XXX Is this what we want in the long term?
            response = request.response
            response.handleException(exc_info)
            return
        finally:
            # Avoid leaking
            exc_info = 0


    def _parameterSetskin(self, pname, pval, request):
        request.setViewSkin(pval)
        
