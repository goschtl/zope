##############################################################################
#
# Copyright (c) 2012 Zope Foundation and Contributors.
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
import zope.interface
import zope.interface.declarations
import martian
import fanstatic.core
import grokcore.resource.interfaces

def validateResources(directive, *resources):
    for resource in resources:
        if not isinstance(resource, fanstatic.core.Dependable):
            raise ValueError(
                'You can only include fanstatic Dependable '
                '(Resource or Group) components.')

class resources(martian.Directive):
    scope = martian.CLASS
    store = martian.MULTIPLE
    validate = validateResources

    def factory(self, *resources):
        zope.interface.declarations.addClassAdvisor(
            _resources_advice, depth=3)
        return resources

def _resources_advice(cls):
    if resources.bind().get(cls):
        if not grokcore.resource.interfaces.IResourcesIncluder.implementedBy(
                cls):
            zope.interface.classImplements(
                cls,
                grokcore.resource.interfaces.IResourcesIncluder)
    return cls
