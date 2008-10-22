##############################################################################
#
# Copyright (c) 2008 Zope Corporation and Contributors.
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
"""Helper functions for zope.introspector.
"""
import types
import inspect
import pkg_resources
from zope.interface import implementedBy
from zope.security.proxy import isinstance, removeSecurityProxy
from martian.scan import resolve as ext_resolve

def resolve(obj_or_dotted_name):
    """Get an object denoted by a dotted name.
    """
    if not isinstance(obj_or_dotted_name, basestring):
        return obj_or_dotted_name
    return ext_resolve(obj_or_dotted_name)
    
def is_namespace_package(dotted_name):
    """Tell, whether a dotted name denotes a namespace package.
    """
    return dotted_name in pkg_resources._namespace_packages.keys()

def get_package_items(dotted_name):
    """Get the items of a package, that is modules, subpackages, etc.

    Delivers names of subpackages, modules, .txt, .rst and .zcml files.
    
    Supports also namespace packages.
    Supports also zipped eggs.
    """
    if is_namespace_package(dotted_name):
        return get_namespace_package_items(dotted_name)
    resources = pkg_resources.resource_listdir(dotted_name, '')
    result = []
    for res in resources:
        if res.startswith('.'):
            # Ignore hidden files and directories.
            continue
        if pkg_resources.resource_isdir(dotted_name, res):
            if pkg_resources.resource_exists(
                dotted_name, res + '/__init__.py'):
                result.append(res)
                continue
        if not '.' in res:
            continue
        name, ext = res.rsplit('.', 1)
        if name == '__init__':
            continue
        if ext.lower() == 'py':
            result.append(name)
        if ext.lower() in ['txt', 'rst', 'zcml']:
            result.append(res)
    return result

def get_namespace_package_items(dotted_name):
    """Get subpackages of a namespace package.
    """
    ws = pkg_resources.working_set
    pkg_names = []
    for entry in ws.entry_keys.values():
        pkg_names.extend(entry)
    result = []
    for name in pkg_names:
        if not name.startswith(dotted_name):
            continue
        name = name.split(dotted_name)[1]
        if '.' in name:
            name = name.split('.')[1]
        result.append(name)
    result = list(set(result)) # make entries unique
    return result

def get_function_signature(func):
    """Return the signature of a function or method."""
    if not isinstance(func, (types.FunctionType, types.MethodType)):
        raise TypeError("func must be a function or method")

    args, varargs, varkw, defaults = inspect.getargspec(func)
    placeholder = object()
    sig = '('
    # By filling up the default tuple, we now have equal indeces for
    # args and default.
    if defaults is not None:
        defaults = (placeholder,)*(len(args)-len(defaults)) + defaults
    else:
        defaults = (placeholder,)*len(args)

    str_args = []

    for name, default in zip(args, defaults):
        # Neglect self, since it is always there and not part of the
        # signature.  This way the implementation and interface
        # signatures should match.
        if name == 'self' and type(func) == types.MethodType:
            continue

        # Make sure the name is a string
        if isinstance(name, (tuple, list)):
            name = '(' + ', '.join(name) + ')'
        elif not isinstance(name, str):
            name = repr(name)

        if default is placeholder:
            str_args.append(name)
        else:
            str_args.append(name + '=' + repr(default))

    if varargs:
        str_args.append('*'+varargs)
    if varkw:
        str_args.append('**'+varkw)

    sig += ', '.join(str_args)
    return sig + ')'

def get_attributes(obj, public_only=True):
    """Return a list of attribute names.

    If `public_only` is set to `False` also attributes, whose names
    start with an underscore ('_') are returned.

    Taken from ``zope.app.apidoc`` with some modifications.
    """
    attrs = []
    for attr in dir(obj):
        if attr.startswith('_') and public_only is True:
            continue
        try:
            getattr(obj, attr)
        except:
            continue
        attrs.append(attr)
    return sorted(attrs)

_marker = object()

def get_python_path(obj):
    """Return the path of the object in standard Python notation.

    This method should try very hard to return a string, even if it is not a
    valid Python path.

    Taken from ``zope.app.apidoc``.
    """
    if obj is None:
        return None

    # Even for methods `im_class` and `__module__` is not allowed to be
    # accessed (which is probably not a bad idea). So, we remove the security
    # proxies for this check.
    naked = removeSecurityProxy(obj)
    if hasattr(naked, "im_class"):
        naked = naked.im_class
    module = getattr(naked, '__module__', _marker)
    if module is _marker:
        return naked.__name__
    return '%s.%s' %(module, naked.__name__)

def get_interface_for_attribute(name, interfaces=_marker, klass=_marker,
                                as_path=True):
    """Determine the interface in which an attribute is defined.

    Taken from ``zope.app.apidoc``.
    """
    if (interfaces is _marker) and (klass is _marker):
        raise ValueError("need to specify interfaces or klass")
    if (interfaces is not _marker) and (klass is not _marker):
        raise ValueError("must specify only one of interfaces and klass")

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
            if as_path:
                return get_python_path(interface)
            return interface

    return None
