##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""mail ZCML Namespace handler 

$Id: metaconfigure.py,v 1.1 2003/04/16 13:45:43 srichter Exp $
"""
from zope.component import getService
from zope.configuration.action import Action
from zope.app.component.metaconfigure import provideService


def mailservice(_context, class_, permission, name="Mail",
                hostname="localhost", port=25, username=None, password=None):

    component = _context.resolve(class_)()
    component.hostname = hostname
    component.port = int(port)
    component.username = username
    component.password = password

    return [
        Action(
            discriminator = ('service', name),
            callable = provideService,
            args = (name, component, permission),
            )
        ]


def mailer(_context, name, class_, serviceType="Mail", default=False):
    klass = _context.resolve(class_)

    if default == "True":
        default = True

    def register(serviceType, name, klass, default): 
        mailservice = getService(None, serviceType)
        mailservice.provideMailer(name, klass, default)
        

    return [
        Action(
             discriminator = ('mailer', name),
             callable = register,
             args = (serviceType, name, klass, default)
             )
        ]
