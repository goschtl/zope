##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""Package Implementation

$Id$
"""
__docformat__ = "reStructuredText"
import zope.interface
from zope.schema import fieldproperty
from zope.app.component import registration
from zope.app.container import btree, contained
from zope.webdev import interfaces


class Package(registration.RegisterableContainer,
              btree.BTreeContainer,
              contained.Contained):
    """A WebDev Package."""
    zope.interface.implements(interfaces.IPackage)

    # See interfaces.IPackage
    docstring = fieldproperty.FieldProperty(interfaces.IPackage['docstring'])

    version = fieldproperty.FieldProperty(interfaces.IPackage['version'])

    license = fieldproperty.FieldProperty(interfaces.IPackage['license'])

    author = fieldproperty.FieldProperty(interfaces.IPackage['author'])

    def __init__(self, name=None, docstring=None, version=None,
                 license=None, author=None):
        super(Package, self).__init__()
        self.__name__, self.docstring, self.version = name, docstring, version
        self.license, self.author = license, author

    @property
    def name(self):
        return self.__name__

    def __repr__(self):
        return '<%s %r>' %(self.__class__.__name__, self.name)
