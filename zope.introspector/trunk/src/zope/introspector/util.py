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
import pkg_resources
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
                dotted_name + '.' + res, '__init__.py'):
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
