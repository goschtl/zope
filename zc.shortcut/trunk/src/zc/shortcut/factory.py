##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
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

from zope import interface, event, component
import zope.component.factory
from zope.app.container.interfaces import INameChooser, IContainer
from zope.app.container.constraints import checkObject
from zope.lifecycleevent import ObjectCreatedEvent

from zc.shortcut import interfaces, Shortcut

class Factory(zope.component.factory.Factory):
    interface.implements(interfaces.IShortcutFactory)

    def __init__(self, *args, **kw):
        shortcut_factory = kw.pop("shortcut_factory", None)
        if shortcut_factory is None:
            shortcut_factory = Shortcut
        self._shortcut_factory = shortcut_factory
        super(Factory, self).__init__(*args, **kw)

    def __call__(self, *args, **kw):
        content = self._callable(*args, **kw)
        event.notify(ObjectCreatedEvent(content))
        repository = component.getAdapter(
            content, IContainer, interfaces.REPOSITORY_NAME)
        chooser = INameChooser(repository)
        name = chooser.chooseName('', content)
        checkObject(repository, name, content)
        repository[name] = content
        # __getitem__ gets the ContainedProxy, if it was used
        return self._shortcut_factory(repository[name])

    def getInterfaces(self):
        return interface.implementedBy(self._shortcut_factory)

    def getTargetInterfaces(self):
        return super(Factory, self).getInterfaces()
