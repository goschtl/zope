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
"""

$Id: HTTPPublicationTraverse.py,v 1.2 2002/06/10 23:29:21 jim Exp $
"""

from Zope.ComponentArchitecture import getView
from Zope.Security.SecurityManagement import getSecurityManager
from Zope.Publisher.Exceptions import NotFound
from types import StringTypes
from Zope.Proxy.ContextWrapper import ContextWrapper

class DuplicateNamespaces(Exception):
    """More than one namespace was specified in a request"""

    
class UnknownNamespace(Exception):
    """A parameter specified an unknown namespace"""


class ExcessiveWrapping(NotFound):
    """Too many levels of acquisition wrapping. We don't beleive them."""



class HTTPPublicationTraverse:
    """ """

    # XXX WE REALLY SHOULD USE INTERFACES HERE


    def getViewFromObject(self, object, name, request): 
        raise NotImplementedError
    

    def traverseName(self, request, ob, name):

        nm = name # the name to look up the object with

        if name.find(';'):
            # Process URI segment parameters. It makes sense to centralize
            # this here. Later it may be abstracted and distributed again,
            # but, if so it will be distributed to various path
            # traversers, rather than to traversal adapters/views.
            ns = ''
            parts = name.split(';')
            nm = parts[:1]
            for param in parts[1:]:
                l = param.find('=')
                if l >= 0:
                    pname = param[:l]
                    pval = param[l+1:]
                    if pname == 'ns':
                        if ns:
                            raise DuplicateNamespaces(name)
                        ns = pval
                    else:
                        pset = getattr(self, "_parameterSet%s" % pname,
                                       self # marker
                                       )
                        if pset is self:
                            # We don't know about this one, so leave it in the
                            # name
                            nm.append(param)
                        else:
                            pset(pname, pval, request)
                else:
                    if ns:
                        raise DuplicateNamespaces(name)
                    ns = param

            nm = ';'.join(nm)
            if ns:
                traverse = getattr(self, "_traverse%s" % ns,
                                   self # marker
                                   )
                if traverse is self:
                    raise UnknownNamespace(ns, name)

                ob2 = traverse(request, ob, nm)
                return ContextWrapper(ob2, ob, name=name)
            elif not nm:
                # Just set params, so skip
                return ob

        if nm == '.':
            return ob
                
        ob2 = self.getViewFromObject(ob, name, request)

        return ContextWrapper(ob2, ob, name=name)

    def _traverseview(self, request, ob, name):
        r = getView(ob, name, request, self)
        if r is self: 
            raise NotFound(ob, name, request)
        return r


    def _traverseetc(self, request, ob, name):
        # XXX
        
        # This is here now to allow us to get service managers from a
        # separate namespace from the content. We add and etc
        # namespace to allow us to handle misc objects.  We'll apply
        # YAGNI for now and hard code this. We'll want something more
        # general later. We were thinking of just calling "get"
        # methods, but this is probably too magic. In particular, we
        # will treat returned objects as sub-objects wrt security and
        # not all get methods may satisfy this assumption. It might be
        # best to introduce some sort of etc registry.

        if name != 'Services':
            raise NotFound(ob, name, request)
            
        
        method_name = "getServiceManager"
        method = getattr(ob, method_name, self)
        if method is self: 
            raise NotFound(ob, name, request)
        # Check access
        ContextWrapper(method, ob, name=name)

        return method()


    def _traverseacquire(self, request, ob, name):
        i = 0
        while i < 200:
            i = i + 1
            r = getattr(ob, name, self)
            if r is not self:
                return r
            r = getcontext(ob)
            if r is None:
                raise NotFound(ob, name, request)
        raise ExcessiveWrapping(ob, name, request)



class HTTPPublicationTraverser(HTTPPublicationTraverse):    

    def traversePath(self, request, ob, path):

        if isinstance(path, StringTypes):
            path = path.split('/')
            if len(path) > 1 and not path[-1]:
                # Remove trailing slash
                path.pop()
        else:
            path = list(path)

        # Remove dingle dots
        path = [x for x in path if x != '.']

        path.reverse()

        # Remove double dots
        while '..' in path:
            l = path.index('..')
            if l < 0 or l+2 > len(path):
                break
            del path[l:l+2]
                     
        pop = path.pop

        while path:
            name = pop()
            ob = self.traverseName(request, ob, name)

        return ob
