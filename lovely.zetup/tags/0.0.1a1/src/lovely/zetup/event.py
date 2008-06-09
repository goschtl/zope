##############################################################################
#
# Copyright (c) 2007 Lovely Systems and Contributors.
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
"""
$Id$
"""
from zope import component
from zope import interface
import interfaces
from zope.app.container.interfaces import IObjectAddedEvent
from z3c.configurator import configurator

@component.adapter(interfaces.IConfigurableSite,
                   IObjectAddedEvent)
def applyConfigurators(obj, event):
    cfg = interfaces.ISiteConfig(obj).config
    configurators = cfg.get('configurators')
    if configurators is not None:
        configurator.configure(obj, configurators, names=configurators.keys(),
                               useNameSpaces=True)
