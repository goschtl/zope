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
"""ContentWorkflow Manager views
 
$Id: contentworkflow.py,v 1.3 2004/03/06 04:17:26 garrett Exp $
"""
from zope.app.introspector import interfaceToName
from zope.app.component.interface import nameToInterface
from zope.app.component.interfacefield import InterfaceField
from zope.app.i18n import ZopeMessageIDFactory as _
from zope.app.form.utility import setUpWidgets
from zope.app.services.servicenames import Workflows
from zope.app.interfaces.form import IInputWidget
from zope.component import getService
from zope.interface import Interface
from zope.publisher.browser import BrowserView
from zope.schema.vocabulary import VocabularyListField
from zope.security.proxy import trustedRemoveSecurityProxy 

__metaclass__ = type
 

class ContentWorkflowsManagerView:
 
    def getName(self):
        return """I'm a ContentWorkflows Utility"""


class IContentProcessMapping(Interface):

    iface = InterfaceField(
        title=u"Content Interface",
        description=u"Specifies the interface that characterizes a particular "
                    u"content type. Select one interface at a time.",
        required=True)
    
    name = VocabularyListField(
        title = u"Process Definition Name",
        description = u"The name of the process that will be available for "
                      u"this content type. Feel free to select several at "
                      u"once.",
        required = True,
        vocabulary = "ProcessDefinitions")


class ManageContentProcessRegistry(BrowserView):

    def __init__(self, *args):
        super(ManageContentProcessRegistry, self).__init__(*args)
        setUpWidgets(self, IContentProcessMapping, IInputWidget)
        self.process_based = int(self.request.get('process_based', '1'))

    def getProcessInterfacesMapping(self):
        mapping = []
        wf = getService(self.context, Workflows)
        for name in wf.getProcessDefinitionNames():
            ifaces = self.context.getInterfacesForProcessName(name)
            ifaces = map(lambda i: interfaceToName(self.context, i), ifaces)
            if ifaces:
                mapping.append({'name': name, 'ifaces': ifaces})
        return mapping

    def getInterfaceProcessesMapping(self):
        mapping = []
        # Nothing bad here; we just read the registry data
        registry = trustedRemoveSecurityProxy(self.context)._registry
        for iface, names in registry.items(): 
            mapping.append({'iface': interfaceToName(self.context, iface),
                            'names': names})
        return mapping

    def update(self):
        status = ''
        if 'ADD' in self.request:
            for name in self.name_widget.getInputValue():
                self.context.register(self.iface_widget.getInputValue(), name)
            status = _('Mapping(s) added.')
        elif 'REMOVE' in self.request:
            mappings = self.request.get('mappings', [])
            for entry in mappings:
                split = entry.rfind(':')
                name = entry[:split]
                iface = nameToInterface(self.context, entry[split+1:])
                self.context.unregister(iface, name)
            status = _('Mapping(s) removed.')
        elif 'SWITCH' in self.request:
            self.request.response.setCookie('process_based',
                                            self.request.get('other_view'))
            self.process_based = int(self.request.get('other_view'))

        return status
