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

from new import instancemethod

from zope.interface import providedBy
from zope.location.interfaces import ILocationInfo
from zope.publisher.interfaces import IRequest
from zope.security.proxy import removeSecurityProxy
import transaction

from zope.pipeline.envkeys import REQUEST_KEY
from zope.pipeline.envkeys import TRAVERSED_KEY


class TransactionScrubber(object):
    """WSGI application that scrubs transaction state.

    Aborts the transaction on the way in and on the way out.
    """

    def __init__(self, next_app):
        self.next_app = next_app

    def __call__(self, environ, start_response):
        transaction.abort()
        try:
            res = self.next_app(environ, start_response)
        finally:
            transaction.abort()


class TransactionController(object):
    """WSGI application that begins and commits/aborts transactions.

    Also annotates the transaction.  Requires 'zope.pipeline.request'
    and 'zope.pipeline.traversed' in the environment.
    """

    def __init__(self, next_app):
        self.next_app = next_app

    def __call__(self, environ, start_response):
        transaction.begin()
        try:
            res = self.next_app(environ, start_response)
        except:
            transaction.abort()
            raise
        txn = transaction.get()
        if txn.isDoomed():
            txn.abort()
        else:
            request = environ[REQUEST_KEY]
            name, ob = environ[TRAVERSED_KEY][-1]
            self.annotate(txn, request, ob)
            txn.commit()
        return res

    def annotate(self, txn, request, ob):
        """Set some useful meta-information on the transaction.

        This information is used by the undo framework, for example.
        """
        if request.principal is not None:
            txn.setUser(request.principal.id)

        # Work around methods that are usually used for views
        bare = removeSecurityProxy(ob)
        if isinstance(bare, instancemethod):
            ob = bare.im_self

        # set the location path
        path = None
        location = ILocationInfo(ob, None)
        if location is not None:
            # Views are made children of their contexts, but that
            # doesn't necessarily mean that we can fully resolve the
            # path. E.g. the family tree of a resource cannot be
            # resolved completely, as the site manager is a dead end.
            try:
                path = location.getPath()
            except (AttributeError, TypeError):
                pass
        if path is not None:
            txn.setExtendedInfo('location', path)

        # set the request type
        iface = IRequest
        for iface in providedBy(request):
            if iface.extends(IRequest):
                break
        iface_dotted = '%s.%s' % (iface.__module__, iface.getName())
        txn.setExtendedInfo('request_type', iface_dotted)
        return txn
