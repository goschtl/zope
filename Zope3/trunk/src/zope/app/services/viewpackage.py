##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""View package.

$Id: viewpackage.py,v 1.8 2003/03/19 19:57:31 alga Exp $
"""
__metaclass__ = type

from zope.app.container.btree import BTreeContainer
from zope.app.interfaces.services.view import IZPTTemplate
from zope.publisher.interfaces.browser import IBrowserPresentation
from zope.app.traversing import getPath, traverse
from zope.proxy.context import getItem, getAttr
from zope.proxy.context import ContextMethod
from zope.app.interfaces.services.configuration import Active
from zope.app.services.configurationmanager \
     import ConfigurationManager
from zope.app.services.configuration import ConfigurationStatusProperty
from zope.proxy.introspection import removeAllProxies
from zope.app.services.view import PageConfiguration
from zope.app.interfaces.services.service import IViewPackage

class ViewPackage(BTreeContainer):

    __implements__ = IViewPackage

    presentationType = IBrowserPresentation
    layer = "default"
    description = ''
    title = ''
    factoryName = None
    attribute = None
    template = None

    def __init__(self):
        super(ViewPackage, self).__init__()
        super(ViewPackage, self).setObject('configure', ConfigurationManager())

    def setObject(self, name, object):
        if not IZPTTemplate.isImplementedBy(object):
            raise TypeError("Can only add templates", object)

        # super() does not work on a context wrapped instance
        base = removeAllProxies(self)

        name = super(ViewPackage, base).setObject(name, object)
        template = getItem(self, name)
        template = getPath(template)
        config = PageConfiguration(
            forInterface=self.forInterface,
            viewName=name,
            permission=self.permission,
            class_=self.factoryName,
            template=template,
            layer=self.layer,
            )
        configure = traverse(self, 'configure')
        id = configure.setObject('', config)
        config = getItem(configure, id)
        config.status = Active
        return name

    setObject = ContextMethod(setObject)

    def configured(self):
        return (hasattr(self, 'permission')
                and hasattr(self, 'forInterface')
                )

    def activated(self):
        "See IConfiguration"

    def deactivated(self):
        "See IConfiguration"
