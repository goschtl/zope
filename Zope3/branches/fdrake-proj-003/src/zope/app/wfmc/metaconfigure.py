##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""WFMC metaconfigure

$Id: $
"""
__docformat__ = "reStructuredText"
from zope import wfmc
from zope.wfmc import xpdl
from zope.app.component.metaconfigure import utility

def defineXpdl(_context, file, process, id):
    package = xpdl.read(open(file))
    definition = package[process]
    definition.id = id

    utility(_context, wfmc.interfaces.IProcessDefinition, definition, name=id)
