##############################################################################
#
# Copyright (c) 2001, 2002, 2008 Zope Foundation and Contributors.
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
"""CMF portal traverser

$Id: traverser.py 67630 2006-04-27 00:54:03Z jim $
"""
__docformat__ = 'restructuredtext'

from zExceptions import Forbidden

from Acquisition import aq_base
from Acquisition.interfaces import IAcquirer

from zope.interface import implements, Interface
from zope.component import queryMultiAdapter
from zope.publisher.interfaces.browser import IBrowserPublisher

from ZPublisher.BaseRequest import DefaultPublishTraverse, typeCheck

class PortalRootPublishTraverse(DefaultPublishTraverse):

    implements(IBrowserPublisher)
        
    def publishTraverse(self, request, name):
        object = self.context
        URL=request['URL']
        

        if name[:1]=='_':
            raise Forbidden("Object name begins with an underscore at: %s" % URL)

        
        if hasattr(object,'__bobo_traverse__'):
            # We can use the normal logic
            return super(PortalRootPublishTraverse, self).publishTraverse(request, name)
        else:
            
            subobject = None
            
            # No __bobo_traverse__
            # Try with an unacquired attribute:
            try:
                subobject = object.__getattribute__(name)
            except AttributeError:
                # this is not a direct object
                pass
            else:
                if IAcquirer.providedBy(subobject):
                    subobject = aq_base(subobject).__of__(object)
            
            if subobject is None:
                # We try to fall back to a view:
                subobject = queryMultiAdapter((object, request), Interface,
                                              name)
                if subobject is not None:
                    if IAcquirer.providedBy(subobject):
                        subobject = subobject.__of__(object)
                    return subobject
            
                # And lastly, of there is no view, try acquired attributes, but
                # only if there is no __bobo_traverse__:
                try:
                    subobject=getattr(object, name)
                    # Again, clear any error status created by __bobo_traverse__
                    # because we actually found something:
                    request.response.setStatus(200)
                    return subobject
                except AttributeError:
                    pass

                # Lastly we try with key access:
                try:
                    subobject = object[name]
                except TypeError: # unsubscriptable
                    raise KeyError(name)
                

        # Ensure that the object has a docstring, or that the parent
        # object has a pseudo-docstring for the object. Objects that
        # have an empty or missing docstring are not published.
        doc = getattr(subobject, '__doc__', None)
        if doc is None:
            doc = getattr(object, '%s__doc__' % name, None)
        if not doc:
            raise Forbidden(
                "The object at %s has an empty or missing " \
                "docstring. Objects must have a docstring to be " \
                "published." % URL
                )

        # Hack for security: in Python 2.2.2, most built-in types
        # gained docstrings that they didn't have before. That caused
        # certain mutable types (dicts, lists) to become publishable
        # when they shouldn't be. The following check makes sure that
        # the right thing happens in both 2.2.2+ and earlier versions.

        if not typeCheck(subobject):
            raise Forbidden(
                "The object at %s is not publishable." % URL
                )

        return subobject
