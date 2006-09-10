##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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

import zope.wfmc.xpdl

import z3c.wfmcpersistent.process

class XPDLHandler(zope.wfmc.xpdl.XPDLHandler):

    ProcessDefinitionFactory = z3c.wfmcpersistent.process.ProcessDefinition
    ParticipantFactory = z3c.wfmcpersistent.process.Participant
    ApplicationFactory = z3c.wfmcpersistent.process.Application
    ActivityDefinitionFactory = z3c.wfmcpersistent.process.ActivityDefinition
    TransitionDefinitionFactory = z3c.wfmcpersistent.process.TransitionDefinition
    
def read(file):
    src = xml.sax.xmlreader.InputSource(getattr(file, 'name', '<string>'))
    src.setByteStream(file)
    parser = xml.sax.make_parser()
    package = zope.wfmc.xpdl.Package()
    parser.setContentHandler(XPDLHandler(package))
    parser.setFeature(xml.sax.handler.feature_namespaces, True)
    parser.parse(src)
    
    return package