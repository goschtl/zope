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

$Id: pagefolder.py,v 1.10 2003/06/05 12:03:17 stevea Exp $
"""
__metaclass__ = type

from zope.app.container.btree import BTreeContainer
from zope.app.container.zopecontainer import ZopeContainerDecorator
from zope.app.interfaces.services.view import IZPTTemplate
from zope.publisher.interfaces.browser import IBrowserPresentation
from zope.app.traversing import getPath
from zope.app.context import getItem
from zope.context import ContextMethod
from zope.app.interfaces.services.configuration import Active
from zope.app.services.configuration import ConfigurationManagerContainer
from zope.proxy import removeAllProxies
from zope.app.services.view import PageConfiguration
from zope.app.interfaces.services.pagefolder import IPageFolder
from zope.app.interfaces.services.configuration import IConfigurationManager
from zope.app.interfaces.file import IDirectoryFactory
from zope.app.fssync.classes import ObjectEntryAdapter, AttrMapping
from zope.app.interfaces.fssync import IObjectDirectory
from zope.interface import implements

class PageFolder(ConfigurationManagerContainer, BTreeContainer):

    implements(IPageFolder)

    presentationType = IBrowserPresentation
    layer = "default"
    description = ''
    title = ''
    factoryName = None
    attribute = None
    template = None

    def setObject(self, name, object):
        if (IConfigurationManager.isImplementedBy(object) or
            IZPTTemplate.isImplementedBy(object)):
            return super(PageFolder, self).setObject(name, object)
        else:
            raise TypeError("Can only add templates", object)

    def configured(self):
        return (hasattr(self, 'permission')
                and hasattr(self, 'forInterface')
                )

    def activated(self):
        "See IConfiguration"

    def deactivated(self):
        "See IConfiguration"


_attrNames = (
    'factoryName',
    'forInterface',
    'layer',
    'permission',
    )

class PageFolderAdapter(ObjectEntryAdapter):
    """ObjectFile adapter for PageFolder objects."""

    implements(IObjectDirectory)

    def contents(self):
        return self.context.items()

    def extra(self):
        return AttrMapping(self.context, _attrNames)


class PageFolderFactory:

    implements(IDirectoryFactory)

    def __init__(self, context):
        self.context = context

    def __call__(self, name):
        return PageFolder()

class PageFolderContextDecorator(ZopeContainerDecorator):

    def setObject(self, name, object):
        name = super(PageFolderContextDecorator, self).setObject(name, object)

        # If a template is added, we need to configure it too.
        if IZPTTemplate.isImplementedBy(object):
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


# XXX Backward compatibility. This is needed to support old pickles.
ViewPackage = PageFolder
import sys
sys.modules['zope.app.services.viewpackage'
            ] = sys.modules['zope.app.services.pagefolder']
