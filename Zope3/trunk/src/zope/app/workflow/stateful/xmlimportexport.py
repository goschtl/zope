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
"""Stateful ProcessDefinition XML Import/Export handlers

$Id: xmlimportexport.py,v 1.1 2003/05/08 17:27:19 jack-e Exp $
"""
__metaclass__ = type


from zope.app.pagetemplate.viewpagetemplatefile \
     import ViewPageTemplateFile
from zope.app.interfaces.workflow.stateful \
     import IStatefulProcessDefinition
from zope.app.interfaces.workflow import IProcessDefinitionImportHandler
from zope.app.interfaces.workflow import IProcessDefinitionExportHandler
from zope.component import getAdapter, getServiceManager
from zope.app.interfaces.dublincore import IZopeDublinCore
from types import StringTypes
from zope.proxy.context import ContextMethod
from zope.proxy.introspection import removeAllProxies
from zope.security.checker import CheckerPublic

from xml.sax import parse
from xml.sax.handler import ContentHandler

from zope.app.workflow.stateful.definition import State, Transition



# basic implementation for a format-checker
class XMLFormatChecker(ContentHandler):

    def __init__(self):
        self.__valid = False

    def startElement(self, name, attrs):
        if name == 'workflow' and attrs.get('type',None) == 'StatefulWorkflow':
            self.__valid = True

    def endElement(self, name):
        pass


    def isValid(self):
        return self.__valid




class XMLStatefulImporter(ContentHandler):
    def __init__(self, context, encoding='latin-1'):
        self.context = context
        self.encoding = encoding
    
    def startElement(self, name, attrs):
        handler = getattr(self, 'start' + name.title().replace('-', ''), None)
        if not handler:
            raise ValueError, 'Unknown element %s' % name

        handler(attrs)

    def endElement(self, name):
        handler = getattr(self, 'end' + name.title().replace('-', ''), None)
        if handler:
            handler()

    def noop(*args):
        pass

    startStates      = noop
    startTransitions = noop

    def startWorkflow(self, attrs):
        dc = getAdapter(self.context, IZopeDublinCore)
        dc.title = attrs.get('title', u'')

    def startSchema(self, attrs):
        name = attrs['name'].encode(self.encoding)
        self.context.setRelevantDataSchema(name)

    def startState(self, attrs):
        encoding = self.encoding
        name  = attrs['name'].encode(encoding)
        if name == 'INITIAL':
            state = self.context.getState('INITIAL')
            dc = getAdapter(state, IZopeDublinCore)
            dc.title = attrs.get('title', u'')
        else:
            state = State()
            dc = getAdapter(state, IZopeDublinCore)
            dc.title = attrs.get('title', u'')
            self.context.addState(name, state)

    def startTransition(self, attrs):
        encoding = self.encoding
        name   = attrs['name'].encode(encoding)
        permission = attrs.get('permission', '').encode(encoding)
        if permission == 'zope.Public':
            permission = CheckerPublic
        trans = Transition(source = attrs['sourceState'].encode(encoding),
                           destination = attrs['destinationState'].encode(encoding),
                           condition = attrs.get('condition', '').encode(encoding),
                           script = attrs.get('script', '').encode(encoding),
                           permission = permission,
                           triggerMode = attrs['triggerMode'].encode(encoding))
        dc = getAdapter(trans, IZopeDublinCore)
        dc.title = attrs.get('title', u'')
        self.context.addTransition(name, trans)


        
class XMLImportHandler:

    __implements__ = IProcessDefinitionImportHandler

    # XXX Implementation needs more work !!
    # check if xml-data can be imported and represents a StatefulPD
    def canImport(self, context, data):
        checker = XMLFormatChecker()
        parse(data, checker)
        return bool(IStatefulProcessDefinition.isImplementedBy(context)) \
               and checker.isValid()
    

    def doImport(self, context, data):
        # XXX Manually clean ProcessDefinition ??
        context.clear()
        parse(data, XMLStatefulImporter(context))
    

class XMLExportHandler:

    __implements__ = IProcessDefinitionExportHandler

    template = ViewPageTemplateFile('xmlexport_template.pt')

    def doExport(self, context, process_definition):
        # XXX Not really nice to fake a BrowserView here ....
        self.request = None
        self.process_definition = process_definition
        self.context = context
        return self.template()

    def getDefinition(self):
        return self.process_definition

    def getDublinCore(self, obj):
        return getAdapter(obj, IZopeDublinCore)

    def getPermissionId(self, permission):
        if isinstance(permission, str):
            return permission
        if permission is CheckerPublic:
            return 'zope.Public'
        if permission is None:
            return ''
        return removeAllProxies(permission).getId()

