##############################################################################
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
##############################################################################
"""Use-Configuration view

$Id: useconfiguration.py,v 1.2 2003/03/03 23:16:04 gvanrossum Exp $
"""
__metaclass__ = type

from zope.component import getAdapter, getView
from zope.app.interfaces.services.configuration import IUseConfiguration
from zope.app.traversing import traverse

class UseConfiguration:

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def uses(self):
        component = self.context
        useconfig = getAdapter(component, IUseConfiguration)
        result = []
        for path in useconfig.usages():
            config = traverse(component, path)
            url = getView(config, 'absolute_url', self.request)
            result.append({'name': config.name,
                           'path': path,
                           'url': url(),
                           'status': config.status,
                           })
        return result
