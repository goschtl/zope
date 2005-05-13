# Copyright (C) 2004 by Dr. Dieter Maurer, Eichendorffstr. 23, D-66386 St. Ingbert, Germany

from sys import modules

from Products.PageTemplates.PythonExpr import PythonExpr

from Products.PageTemplates.Expressions import \
     SubPathExpr, PathExpr, \
     StringExpr, \
     getEngine, installHandlers

from ReuseUtils import rebindFunction


class _ModuleImporter:
  def __getitem__(self, module):
    __import__(module)
    return modules[module]
ModuleImporter = _ModuleImporter()


def trustedTraverse(ob, path, ignored,):
  if not path: return self

  get = getattr
  has = hasattr
  N = None
  M = rebindFunction # artifical marker

  if isinstance(path, str): path = path.split('/')
  else: path=list(path)
  
  REQUEST={'TraversalRequestNameStack': path}
  path.reverse()
  pop=path.pop

  if len(path) > 1 and not path[0]:
    # Remove trailing slash
    path.pop(0)

  if not path[-1]:
    # If the path starts with an empty string, go to the root first.
    pop()
    self=ob.getPhysicalRoot()

  object = ob
  while path:
    name=pop()
    __traceback_info__ = path, name

    if name == '..':
      o=getattr(object, 'aq_parent', M)
      if o is not M:
        object=o
        continue

    t=get(object, '__bobo_traverse__', M)
    if t is not M: o=t(REQUEST, name)
    else:
      o = get(object, name, M)
      if o is M:
        try: o = object[name]
        except AttributeError: # better exception
          raise AttributeError(name)
    object = o

  return object


class SubPathExpr(SubPathExpr):
  _eval = rebindFunction(SubPathExpr._eval.im_func,
                         restrictedTraverse=trustedTraverse,
                         )

class PathExpr(PathExpr):
  __init__ = rebindFunction(PathExpr.__init__.im_func,
                            SubPathExpr=SubPathExpr,
                            )

class StringExpr(StringExpr):
  __init__ = rebindFunction(StringExpr.__init__.im_func,
                            PathExpr=PathExpr,
                            )
  
installHandlers = rebindFunction(installHandlers,
                                 PathExpr=PathExpr,
                                 StringExpr=StringExpr,
                                 PythonExpr=PythonExpr,
                                 )

_engine=None
getEngine = rebindFunction(getEngine,
                           _engine=_engine,
                           installHandlers=installHandlers
                           )


