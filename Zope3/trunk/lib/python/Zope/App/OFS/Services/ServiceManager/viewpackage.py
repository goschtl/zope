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

$Id: viewpackage.py,v 1.2 2002/12/19 20:38:25 jim Exp $
"""
__metaclass__ = type

from Zope.App.OFS.Container.BTreeContainer import BTreeContainer
from Zope.App.OFS.Services.interfaces import IZPTTemplate
from Zope.Publisher.Browser.IBrowserPresentation import IBrowserPresentation
from Zope.App.Traversing import getPhysicalPathString, traverse
from Zope.Proxy.ContextWrapper import getItem, getAttr
from Zope.ContextWrapper import ContextMethod
from Zope.App.OFS.Services.ConfigurationInterfaces import Active
from Zope.App.OFS.Services.ServiceManager.ConfigurationManager \
     import ConfigurationManager
from Zope.App.OFS.Services.Configuration import ConfigurationStatusProperty
from Zope.Proxy.ProxyIntrospection import removeAllProxies
from Zope.App.OFS.Services.view import PageConfiguration
from interfaces import IViewPackage

class ViewPackage(BTreeContainer):

    __implements__ = IViewPackage


    presentationType = IBrowserPresentation
    layer = "default"
    description = ''
    title = ''

    def __init__(self):
        super(ViewPackage, self).__init__()
        super(ViewPackage, self).setObject('configure', ConfigurationManager())

    def setObject(self, name, object):
        if not IZPTTemplate.isImplementedBy(object):
            raise TypeError("Can only add packages")
        
        # super() does not work on a context wrapped instance
        base = removeAllProxies(self)

        name = super(ViewPackage, base).setObject(name, object)
        template = getItem(self, name)
        template = getPhysicalPathString(template)
        config = PageConfiguration(self.forInterface, name,
                                   self.presentationType,
                                   self.factoryName, template,
                                   self.layer)
        configure = traverse(self, 'configure')
        id = configure.setObject('', config)
        config = getItem(configure, id)
        config.status = Active
        return name

    setObject = ContextMethod(setObject)

    def activated(self):
        "See Zope.App.OFS.Services.ConfigurationInterfaces.IConfiguration"

    def deactivated(self):
        "See Zope.App.OFS.Services.ConfigurationInterfaces.IConfiguration"

