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

$Id: metadirectives.py,v 1.1 2003/08/01 20:40:59 srichter Exp $
"""
from zope.configuration.fields import GlobalObject
from zope.interface import Interface

class IImportHandlerDirective(Interface):
    """Register an Import Handler, that is able to load a XML Representation
    of a ProcessDefinition and create a persistent Instance for it."""

    interface = GlobalObject(
        title=u"Interface",
        description=u"The interface of the process definition this "\
                    u"handler can load.",
        required=True)

    factory = GlobalObject(
        title=u"Factory",
        description=u"The factory for the instance that implements the "\
                    u"handler.",
        required=True)


class IExportHandlerDirective(Interface):
    """Register an Export Handler, that is able to save a XML Representation
        of a ProcessDefinition from a given object."""

    interface = GlobalObject(
        title=u"Interface",
        description=u"The interface of the process definition this "\
                    u"handler can save.",
        required=True)

    factory = GlobalObject(
        title=u"Factory",
        description=u"The factory for the instance that implements the "\
                    u"handler.",
        required=True)

