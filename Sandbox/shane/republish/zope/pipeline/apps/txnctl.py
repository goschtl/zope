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


import transaction
from zope.location.interfaces import ILocationInfo
from zope.interface import adapts
from zope.interface import implements
from zope.interface import providedBy
from zope.publisher.interfaces import IRequest
from zope.publisher.interfaces import IWSGIApplication
from zope.security.proxy import removeSecurityProxy


class TransactionController(object):
    """WSGI middleware that begins and commits/aborts transactions.
    """
    implements(IWSGIApplication)
    adapts(IWSGIApplication)

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        transaction.begin()
        try:
            res = self.app(environ, start_response)
        except:
            transaction.abort()
            raise
        txn = transaction.get()
        if txn.isDoomed():
            txn.abort()
        else:
            txn.commit()
        return res


class TransactionAnnotator(object):
    """WSGI middleware that annotates transactions.

    Requires 'zope.request' in the environment.
    """
    implements(IWSGIApplication)
    adapts(IWSGIApplication)

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        res = self.app(environ, start_response)
        txn = transaction.get()
        if not txn.isDoomed():
            request = environ['zope.request']
            name, ob = request.traversed[-1]
            self.annotate(txn, request, ob)
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
