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
"""Directive schema for the 'workflow' namespace.

$Id: metadirectives.py,v 1.4 2003/08/02 16:36:54 srichter Exp $
"""
from zope.configuration.fields import GlobalObject
from zope.interface import Interface

class IHandlerDirective(Interface):
    """Register an Import/Export Handler, that is able to load/save a XML
    Representation of a ProcessDefinition and create a persistent Instance for
    it."""

    interface = GlobalObject(
        title=u"Interface",
        description=u"The interface of the process definition this "\
                    u"handler can handle (both for either import or export).",
        required=True)

    factory = GlobalObject(
        title=u"Factory",
        description=u"The factory for the instance that implements the "\
                    u"handler.",
        required=True)
