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

from zope.interface import implements
from zope.publisher.interfaces import IWSGIApplication

from zope.pipeline.envkeys import TRAVERSAL_HOOKS_KEY
from zope.pipeline.envkeys import TRAVERSED_KEY


class Traverser(object):
    """Traverses the object graph based on the traversal stack.

    Requires 'zope.pipeline.traversed' in the WSGI environment. Calls
    the hooks listed in 'zope.pipeline.traversal_hooks', if there are
    any.
    """
    implements(IWSGIApplication)

    def __init__(self, next_app):
        self.next_app = next_app

    def __call__(self, environ, start_response):
        self.traverse(environ)
        return self.next_app(environ, start_response)

    def get_stack(self, environ):
        pass

    def traverse(self, environ):
        stack = self.get_stack(environ)
        traversed = environ[TRAVERSED_KEY]
        hooks = environ.get(TRAVERSAL_HOOKS_KEY, ())

        root_name, obj = traversed[-1]
        prev_object = None

        while True:
            if obj is not prev_object:
                # Call hooks (but not more than once).
                for hook in hooks:
                    hook(request, obj)
                prev_object = obj

            if not stack:
                obj, stack = self.add_steps(environ)
                if stack:
                    # call traversal hooks and traverse some more
                    continue
                else:
                    # done traversing
                    break

            # Traverse the next step.
            name = stack.pop()
            obj = self.traverse_name(obj, name)
            traversed.append((name, obj))

    def traverse_name(self, obj, name):
        pass

    def add_steps(self, environ):
        pass


class HTTPTraverser(Traverser):
    # includes form_action (or should this be in BrowserTraverser?)
    implements(IWSGIApplication)


class BrowserTraverser(HTTPTraverser):
    # includes browserDefault traversal
    implements(IWSGIApplication)

