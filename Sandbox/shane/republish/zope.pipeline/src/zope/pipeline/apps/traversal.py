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

from zope.component import queryMultiAdapter
from zope.publisher.interfaces.browser import IBrowserPublisher
from zope.publisher.interfaces.exceptions import NotFound
from zope.publisher.interfaces import IPublishTraverse
from zope.security.checker import ProxyFactory
from zope.traversing.namespace import namespaceLookup
from zope.traversing.namespace import nsParse

from zope.pipeline.envkeys import DEFAULT_TRAVERSAL_STEPS_KEY
from zope.pipeline.envkeys import REQUEST_KEY
from zope.pipeline.envkeys import TRAVERSAL_HOOKS_KEY
from zope.pipeline.envkeys import TRAVERSED_KEY


class Traverser(object):
    """WSGI app that traverses the path specified by PATH_INFO.

    Requires 'zope.pipeline.request' and 'zope.pipeline.traversed' in
    the WSGI environment. Calls the hooks listed in
    'zope.pipeline.traversal_hooks', if there are any. Appends to
    'zope.pipeline.traversed' and sets
    'zope.pipeline.default_traversal_steps'.
    """

    def __init__(self, next_app):
        self.next_app = next_app
        self.proxy_factory = ProxyFactory

    def __call__(self, environ, start_response):
        self.traverse(environ)
        return self.next_app(environ, start_response)

    def get_steps(self, environ):
        """Return the list of names to traverse.

        The list of names to traverse comes from environ['PATH_INFO'].
        """
        path = environ.get("PATH_INFO", "/")
        steps = []
        for item in path.split('/'):
            if not item or item == '.':
                continue
            elif item == '..':
                try:
                    del steps[-1]
                except IndexError:
                    raise NotFound('..')
            else:
                steps.append(item)
        return steps


    def traverse(self, environ):
        """Traverse the object graph by following URL path segments.

        Updates the traversal variables in the WSGI environment at each step.
        """
        stack = self.get_steps(environ)
        stack.reverse()
        request = environ[REQUEST_KEY]
        traversed = environ[TRAVERSED_KEY]
        hooks = environ.get(TRAVERSAL_HOOKS_KEY, ())
        environ[DEFAULT_TRAVERSAL_STEPS_KEY] = 0

        root_name, obj = traversed[-1]
        prev_object = None
        default_traversal = False

        while True:
            if obj is not prev_object:
                # Call hooks (but not more than once).
                for hook in hooks:
                    hook(request, obj)
                prev_object = obj

            if not stack:
                next_obj, add_steps = self.get_default_traversal(request, obj)
                if add_steps:
                    stack = list(add_steps)
                    stack.reverse()
                    # Now traverse through default traversal steps.
                    # Call traversal hooks and traverse some more.
                    default_traversal = True
                    obj = next_obj
                    continue
                else:
                    # done traversing
                    break

            # Traverse the next step.
            name = stack.pop()
            obj = self.traverse_name(request, obj, name)
            traversed.append((name, obj))
            if default_traversal:
                environ[DEFAULT_TRAVERSAL_STEPS_KEY] += 1


    def traverse_name(self, request, ob, name):
        nm = name # the name to look up the object with

        if name and name[:1] in '@+':
            # Process URI segment parameters.
            ns, nm = nsParse(name)
            if ns:
                try:
                    ob2 = namespaceLookup(ns, nm, ob, request)
                except TraversalError:
                    raise NotFound(ob, name)

                return self.proxy_factory(ob2)

        if nm == '.':
            return ob

        if IPublishTraverse.providedBy(ob):
            ob2 = ob.publishTraverse(request, nm)
        else:
            # self is marker
            adapter = queryMultiAdapter((ob, request), IPublishTraverse,
                                        default=self)
            if adapter is not self:
                ob2 = adapter.publishTraverse(request, nm)
            else:
                raise NotFound(ob, name, request)

        return self.proxy_factory(ob2)


    def get_default_traversal(self, request, ob):
        """Get the default traversal steps for an object.

        Returns (next_object, steps).  
        """
        return ob, None


class BrowserTraverser(Traverser):
    # includes form_action and browserDefault traversal

    def get_steps(self, environ):
        """Return the list of names to traverse.

        This implementation calls super.get_steps(), then if a form
        action was provided, the action is appended to the steps.
        """
        steps = super(BrowserTraverser, self).get_steps(environ)
        request = environ[REQUEST_KEY]
        if request.form_action:
            steps.append(request.form_action)
        return steps

    def get_default_traversal(self, request, ob):
        """Get the default traversal steps for an object.

        Returns (next_object, steps).
        """
        if request.form_action:
            # Do not follow default traversal when a form action was
            # provided.
            return ob, None

        if IBrowserPublisher.providedBy(ob):
            # ob is already proxied, so the result of calling a method
            # will be too.
            return ob.browserDefault(request)

        adapter = queryMultiAdapter((ob, request), IBrowserPublisher)
        if adapter is not None:
            ob, path = adapter.browserDefault(request)
            ob = self.proxy_factory(ob)
            return ob, path

        # ob is already proxied
        return ob, None
