##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Utilties to make the life of Documentation Modules easier.

$Id: utilities.py,v 1.3 2004/03/03 10:38:30 philikon Exp $
"""
import re
import types
import inspect

from zope.interface import implements, implementedBy
from zope.security.checker import getCheckerForInstancesOf
from zope.security.interfaces import INameBasedChecker

from zope.app.container.interfaces import IReadContainer

__metaclass__ = type

_remove_html_overhead = re.compile(
    r'(?sm)^<html.*<body.*?>\n(.*)</body>\n</html>\n')

_marker = object()

class ReadContainerBase:
    """Base for IReadContainer objects.

    This is a base class that minimizes the implementation of IReadContainers
    to two methods, get() and items(), since the other methods can be
    implemented using these two.

    Demonstration::

      Make a sample implementation first

      >>> class Container(ReadContainerBase):
      ...     def get(self, key, default=None):
      ...         return {'a': 1, 'b': 2}.get(key, default)
      ...     def items(self):
      ...         return [('a', 1), ('b', 2)]

      >>> container = Container()

      Now we can use the methods

      >>> container.get('a')
      1
      >>> container.get('c') is None
      True
      >>> container['b']
      2

      >>> container.items()
      [('a', 1), ('b', 2)]
      >>> container.keys()
      ['a', 'b']
      >>> container.values()
      [1, 2]

      >>> 1 in container
      True
      >>> len(container)
      2
    """

    implements(IReadContainer)

    def get(self, key, default=None):
        raise NotImplemented
    
    def items(self):
        raise NotImplemented

    def __getitem__(self, key):
        default = object()
        obj = self.get(key, default)
        if obj is default:
            raise KeyError, key
        return obj

    def __contains__(self, key):
        return self.get(key) is None

    def keys(self):
        return map(lambda x: x[0], self.items())

    def __iter__(self):
        return self.values().__iter__()
        
    def values(self):
        return map(lambda x: x[1], self.items())

    def __len__(self):
        return len(self.items())


def getPythonPath(obj):
    """Return the path of the object in standard Python notation.

    This method makes only sense for classes and interfaces. Instances do not
    have a '__name__' attribute, so we would expect them to fail.

    Example::

      >>> from zope.interface import Interface
      >>> class ISample(Interface):
      ...     pass
      >>> class Sample(object):
      ...     pass

      >>> getPythonPath(ISample)
      'zope.app.apidoc.utilities.ISample'

      >>> getPythonPath(Sample)
      'zope.app.apidoc.utilities.Sample'

      >>> try:
      ...   getPythonPath(Sample())
      ... except AttributeError:
      ...   print 'failed'
      failed
    """
    if obj is None:
        return None
    module = obj.__module__
    return '%s.%s' %(module, obj.__name__)


def stx2html(text, level=1):
    r"""Convert STX text to HTML.

    Example::

      >>> text = 'Header\n\n  Normal text goes here.'

      >>> stx2html(text)
      '<h1>Header</h1>\n<p>  Normal text goes here.</p>\n'

      >>> stx2html(text, level=3)
      '<h3>Header</h3>\n<p>  Normal text goes here.</p>\n'

      >>> stx2html(text, level=6)
      '<h6>Header</h6>\n<p>  Normal text goes here.</p>\n'
    """
    from zope.structuredtext.document import Document
    from zope.structuredtext.html import HTML
    doc = Document()(text)
    html = HTML()(doc, level)
    html = _remove_html_overhead.sub(r'\1', html)
    return html


def getPermissionIds(name, checker=_marker, klass=_marker):
    """Get the permissions of an attribute.

    Either the klass or the checker must be specified. If the class is
    specified, then the checker for it is looked up. Furthermore, this
    function only works with 'INameBasedChecker' checkers. If another checker
    is found, 'None' is returned for the permissions.

    Example::

      We first define the class and then the checker for it

      >>> from zope.security.checker import Checker, defineChecker
      
      >>> class Sample(object):
      ...     attr = 'value'

      >>> class Sample2(object):
      ...      pass

      >>> checker = Checker({'attr': 'zope.Read'}.get,
      ...                   {'attr': 'zope.Write'}.get) 
      >>> defineChecker(Sample, checker)

      Now let's see how this function works

      >>> entries = getPermissionIds('attr', klass=Sample)
      >>> entries['read_perm']
      'zope.Read'
      >>> entries['write_perm']
      'zope.Write'

      >>> entries = getPermissionIds('attr', getCheckerForInstancesOf(Sample))
      >>> entries['read_perm']
      'zope.Read'
      >>> entries['write_perm']
      'zope.Write'

      >>> entries = getPermissionIds('attr2', klass=Sample)
      >>> print entries['read_perm']
      N/A
      >>> print entries['write_perm']
      N/A

      >>> entries = getPermissionIds('attr', klass=Sample2)
      >>> entries['read_perm'] is None
      True
      >>> print entries['write_perm'] is None
      True
    """
    assert (klass is _marker) != (checker is _marker)
    entry = {}
    
    if klass is not _marker:
        checker = getCheckerForInstancesOf(klass)
    
    if checker is not None and \
           INameBasedChecker.isImplementedBy(checker):
        entry['read_perm'] = checker.permission_id(name) or 'N/A'
        entry['write_perm'] = checker.setattr_permission_id(name) or 'N/A'
    else:
        entry['read_perm'] = entry['write_perm'] = None 

    return entry


def getFunctionSignature(func):
    """Return the signature of a function or method.

    The 'func' argument *must* be a generic function or a method of a class. 

    Examples::

      >>> def func(attr, attr2=None):
      ...     pass
      >>> print getFunctionSignature(func)
      (attr, attr2=None)

      >>> def func(attr, **kw):
      ...     pass
      >>> print getFunctionSignature(func)
      (attr, **kw)

      >>> def func(attr, attr2=None, **kw):
      ...     pass      
      >>> print getFunctionSignature(func)
      (attr, attr2=None, **kw)

      >>> def func(*args, **kw):
      ...     pass
      >>> print getFunctionSignature(func)
      (*args, **kw)

      >>> def func(**kw):
      ...     pass
      >>> print getFunctionSignature(func)
      (**kw)

      >>> class Klass(object):
      ...     def func(self, attr):
      ...         pass
      
      >>> print getFunctionSignature(Klass.func)
      (attr)

      >>> class Klass(object):
      ...     def func(self, attr, *args, **kw):
      ...         pass
      
      >>> print getFunctionSignature(Klass.func)
      (attr, *args, **kw)
      
      >>> try:
      ...     getFunctionSignature('func')
      ... except AssertionError:
      ...     print 'Argument not a function or method.'
      Argument not a function or method.
    """
    assert type(func) in (types.FunctionType, types.MethodType)
    
    args, varargs, varkw, default = inspect.getargspec(func)
    placeholder = object()
    sig = '('
    # By filling up the default tuple, we now have equal indeces for args and
    # default.
    if default is not None:
        default = (placeholder,)*(len(args)-len(default)) + default
    else:
        default = (placeholder,)*len(args)

    str_args = []

    for i in range(len(args)):
        # Neglect self, since it is always there and not part of the signature.
        # This way the implementation and interface signatures should match.
        if args[i] == 'self' and type(func) == types.MethodType:
            continue
        if default[i] is placeholder:
            str_args.append(args[i])
        else:
            str_args.append(args[i] + '=' + default[i].__repr__())

    if varargs:
        str_args.append('*'+varargs)
    if varkw:
        str_args.append('**'+varkw)

    sig += ', '.join(str_args)
    return sig + ')'


def getPublicAttributes(obj):
    """Return a list of public attribute names.

    This excludes any attribute starting with '_'. The 'obj' argument can be
    either a classic class, type or instance of the previous two. Note that
    the term "attributes" here includes methods and properties.

    Examples::

      >>> class Sample(object):
      ...     attr = None
      ...     def __str__(self):
      ...         return ''
      ...     def func(self):
      ...         pass
      ...     def _getAttr(self):
      ...         return self.attr
      ...     attr2 = property(_getAttr)
      >>> class Sample2:
      ...     attr = None
      >>> class Sample3(Sample):
      ...     attr3 = None
      
      >>> attrs = getPublicAttributes(Sample)
      >>> attrs.sort()
      >>> print attrs
      ['attr', 'attr2', 'func']
      
      >>> attrs = getPublicAttributes(Sample())
      >>> attrs.sort()
      >>> print attrs
      ['attr', 'attr2', 'func']
      
      >>> attrs = getPublicAttributes(Sample2)
      >>> attrs.sort()
      >>> print attrs
      ['attr']
      
      >>> attrs = getPublicAttributes(Sample3)
      >>> attrs.sort()
      >>> print attrs
      ['attr', 'attr2', 'attr3', 'func']
    """
    attrs = []
    for attr in dir(obj):
        if attr.startswith('_'):
            continue
        else:
            attrs.append(attr)
    return attrs

def getInterfaceForAttribute(name, interfaces=_marker, klass=_marker,
                             asPath=True):
    """Determine the interface in which an attribute is defined.

    This function is nice, if you have an attribute name which you retrieved
    from a class and want to know which interface requires it to be there.

    Either 'interfaces' or 'klass' must be specified. If 'interfaces' is not
    specified, the 'klass' is used to retrieve a list of
    interfaces. 'interfaces' must be iteratable.

    'asPath' specifies whether the dotted name of the interface or the
    interface object is returned.

    If no match is found, 'None' is returned.

    Example::

      >>> from zope.interface import Interface, Attribute
      >>> class I1(Interface):
      ...     attr = Attribute('attr')
      >>> class I2(I1):
      ...     def getAttr():
      ...         '''get attr'''
      >>> class Sample(object):
      ...     implements(I2)

      >>> getInterfaceForAttribute('attr', (I1, I2), asPath=False).getName()
      'I1'
      >>> getInterfaceForAttribute('getAttr', (I1, I2), asPath=False).getName()
      'I2'
      >>> getInterfaceForAttribute('attr', klass=Sample, asPath=False).getName()
      'I1'
      >>> getInterfaceForAttribute(
      ...     'getAttr', klass=Sample, asPath=False).getName()
      'I2'

      >>> getInterfaceForAttribute('attr', (I1, I2))
      'zope.app.apidoc.utilities.I1'

      >>> getInterfaceForAttribute('attr2', (I1, I2)) is None
      True
      >>> getInterfaceForAttribute('attr2', klass=Sample) is None
      True

      >>> try:
      ...     getInterfaceForAttribute('getAttr')
      ... except AssertionError:
      ...     print 'need to specify the interfaces or a klass'
      need to specify the interfaces or a klass

    """
    assert (interfaces is _marker) != (klass is _marker)

    if interfaces is _marker:
        direct_interfaces = list(implementedBy(klass))
        interfaces = {}
        for interface in direct_interfaces:
            interfaces[interface] = 1
            for base in interface.getBases():
                interfaces[base] = 1
        interfaces = interfaces.keys()
        
    for interface in interfaces:
        if name in interface.names():                
            if asPath:
                return getPythonPath(interface)
            return interface

    return None
