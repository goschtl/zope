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
"""Page Folders

Page folders support easy creation and configuration of page views
using folders of templates.

$Id: pagefolder.py,v 1.5 2003/05/01 19:35:34 faassen Exp $
"""
__metaclass__ = type

from zope.app.container.btree import BTreeContainer
from zope.app.interfaces.services.view import IZPTTemplate
from zope.publisher.interfaces.browser import IBrowserPresentation
from zope.app.traversing import getPath
from zope.proxy.context import getItem, ContextMethod
from zope.app.interfaces.services.configuration import Active
from zope.app.services.configuration import ConfigurationManagerContainer
from zope.proxy.introspection import removeAllProxies
from zope.app.services.view import PageConfiguration
from zope.app.interfaces.services.pagefolder import IPageFolder
from zope.app.interfaces.services.configuration import IConfigurationManager

class PageFolder(ConfigurationManagerContainer, BTreeContainer):

    __implements__ = IPageFolder

    presentationType = IBrowserPresentation
    layer = "default"
    description = ''
    title = ''
    factoryName = None
    attribute = None
    template = None

    def setObject(self, name, object):
        if IConfigurationManager.isImplementedBy(object):
            # We allow configuration managers as well as templates
            return super(PageFolder, self).setObject(name, object)

        if not IZPTTemplate.isImplementedBy(object):
            raise TypeError("Can only add templates", object)

        # super() does not work on a context wrapped instance
        base = removeAllProxies(self)

        name = super(PageFolder, base).setObject(name, object)
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
        configure = self.getConfigurationManager()
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

# XXX Backward compatibility. This is needed to support old pickles.
ViewPackage = PageFolder
import sys
sys.modules['zope.app.services.viewpackage'
            ] = sys.modules['zope.app.services.pagefolder']
