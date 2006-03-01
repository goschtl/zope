##############################################################################
#
# Copyright (c) 2004, 2005 Zope Corporation and Contributors.
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
"""A 'PageTemplateFile' without security restrictions.

$Id$
"""
import os, sys

from Globals import package_home
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from zope.app.pagetemplate.viewpagetemplatefile import ViewMapper
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

from Products.Five.browser.ReuseUtils import rebindFunction
from Products.Five.browser.TrustedExpression import getEngine, ModuleImporter

from zope.tales.tales import ExpressionEngine
from zope.tales.expressions import PathExpr, StringExpr, NotExpr, DeferExpr, SubPathExpr
from zope.tales.expressions import SimpleModuleImporter, _marker
from zope.tales.pythonexpr import PythonExpr
from zope.tales.tales import _valid_name, _parse_expr, NAME_RE, Undefined 


def BoboTraverseAwareSimpleTraverse(object, path_items, econtext):
    """ a slightly modified version of zope.tales.expressions.simpleTraverse()
        that interacts correctly with objects implementing bobo_traverse().
    """

    for name in path_items:
        next = getattr(object, name, _marker)
        if next is not _marker:
            object = next
        elif hasattr(object, '__getitem__'):
            try:
                object = object[name]
            except KeyError:
                # deal with traversal through bobo_traverse()
                object = object.restrictedTraverse(name)
        else:
            # Allow AttributeError to propagate
            object = getattr(object, name)
    return object


class PathExpr(PathExpr):
    """We need to subclass PathExpr at this point since there is no other
       away to pass our own traverser because we do not instantiate 
       PathExpr on our own...this sucks!
    """

    def __init__(self, name, expr, engine, traverser=BoboTraverseAwareSimpleTraverse):
        self._s = expr
        self._name = name
        paths = expr.split('|')
        self._subexprs = []
        add = self._subexprs.append
        for i in range(len(paths)):
            path = paths[i].lstrip()
            if _parse_expr(path):
                # This part is the start of another expression type,
                # so glue it back together and compile it.
                add(engine.compile('|'.join(paths[i:]).lstrip()))
                break
            add(SubPathExpr(path, traverser, engine)._eval)


def Engine():
    e = ExpressionEngine()
    reg = e.registerType
    for pt in PathExpr._default_type_names:
        reg(pt, PathExpr)
    reg('string', StringExpr)
    reg('python', PythonExpr)
    reg('not', NotExpr)
    reg('defer', DeferExpr)
    e.registerBaseName('modules', SimpleModuleImporter())
    return e

Engine = Engine()


class ZopeTwoPageTemplateFile(PageTemplateFile):
    """A strange hybrid between Zope 2 and Zope 3 page template.

    Uses Zope 2's engine, but with security disabled and with some
    initialization and API from Zope 3.
    """
        
    def __init__(self, filename, _prefix=None, content_type=None):
        # XXX doesn't use content_type yet
        
        self.ZBindings_edit(self._default_bindings)

        path = self.get_path_from_prefix(_prefix)
        self.filename = os.path.join(path, filename)
        if not os.path.isfile(self.filename):
            raise ValueError("No such file", self.filename)

        basepath, ext = os.path.splitext(self.filename)
        self.__name__ = os.path.basename(basepath)


        # required for the ajung-zpt-final-integration branch
        try:
            PageTemplateFile.__init__(self, self.filename, _prefix)
        except:
            pass
        
 
    def get_path_from_prefix(self, _prefix):
        if isinstance(_prefix, str):
            path = _prefix
        else:
            if _prefix is None:
                _prefix = sys._getframe(2).f_globals
            path = package_home(_prefix)
        return path 

    _cook = rebindFunction(PageTemplateFile._cook,
                           getEngine=getEngine)
    
    pt_render = rebindFunction(PageTemplateFile.pt_render,
                               getEngine=getEngine)

    def pt_getEngine(self):
        return Engine
    
    def _pt_getContext(self):
        try:
            root = self.getPhysicalRoot()
            view = self._getContext()
        except AttributeError:
            # self has no attribute getPhysicalRoot. This typically happens 
            # when the template has no proper acquisition context. 
            # That also means it has no view.  /regebro
            root = self.context.getPhysicalRoot()
            view = None

        here = self.context.aq_inner

        request = getattr(root, 'REQUEST', None)
        c = {'template': self,
             'here': here,
             'context': here,
             'container': here,
             'nothing': None,
             'options': {},
             'root': root,
             'request': request,
             'modules': ModuleImporter,
             }
        if view:
            c['view'] = view
            c['views'] = ViewMapper(here, request)

        return c

    pt_getContext = rebindFunction(_pt_getContext,
                                   SecureModuleImporter=ModuleImporter)
