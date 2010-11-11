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
"""XPDL reader for persistent process definitions

$Id: xpdl.py 38178 2005-08-30 21:50:19Z mj $
"""

import xml.sax
import xml.sax.xmlreader
import xml.sax.handler

from persistent.dict import PersistentDict

from zope.interface import implements

import zope.wfmc.xpdl

from z3c.wfmcpersistent.interfaces import IExtendedAttribute
import z3c.wfmcpersistent.process

class XPDLHandler(zope.wfmc.xpdl.XPDLHandler):

    ProcessDefinitionFactory = z3c.wfmcpersistent.process.ProcessDefinition
    ParticipantFactory = z3c.wfmcpersistent.process.Participant
    ApplicationFactory = z3c.wfmcpersistent.process.Application
    ActivityDefinitionFactory = z3c.wfmcpersistent.process.ActivityDefinition
    TransitionDefinitionFactory = z3c.wfmcpersistent.process.TransitionDefinition
    
    def __init__(self, package):
        zope.wfmc.xpdl.XPDLHandler.__init__(self, package)
        self.start_handlers[(zope.wfmc.xpdl.xpdlns,
                             'ExtendedAttribute')] = \
                             XPDLHandler.ExtendedAttributeHnd
        self.end_handlers[(zope.wfmc.xpdl.xpdlns,
                           'ExtendedAttribute')] = \
                           XPDLHandler.extendedattributeHnd
        
    def ExtendedAttributeHnd(self, attrs):
        name = attrs.get((None, 'Name'))
        value = attrs.get((None, 'Value'))
        return ExtendedAttribute(name, value)
    
    def extendedattributeHnd(self, eattribute):
        obj = self.stack[-1]
        if not hasattr(obj, 'ExtendedAttributes'):
            obj.ExtendedAttributes = PersistentDict()
        complex = self.text.strip()
        eattribute.content = complex
        obj.ExtendedAttributes[eattribute.__name__]=eattribute

class ExtendedAttribute(object):
    implements(IExtendedAttribute)
    
    def __init__(self, name, value=None):
        self.__name__ = name
        self.value = value
        self.content = None

def read(file):
    src = xml.sax.xmlreader.InputSource(getattr(file, 'name', '<string>'))
    src.setByteStream(file)
    parser = xml.sax.make_parser()
    package = zope.wfmc.xpdl.Package()
    parser.setContentHandler(XPDLHandler(package))
    parser.setFeature(xml.sax.handler.feature_namespaces, True)
    parser.parse(src)
    
    return package