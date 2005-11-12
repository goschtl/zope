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
"""Tutorials-related Interfaces

$Id$
"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.schema
from zope.app.container import interfaces


class ITutorialManager(interfaces.IReadContainer):
    """Tutorial Manager

    The tutorial manager is used as an entry point to the tutorials
    application.
    """


class ITutorial(zope.interface.Interface):
    """Tutorial

    Tutorials are objects that provide a tutorial via the browser to a
    user. They use functional test-browser tests for their content.
    """

    title = zope.schema.TextLine(
        title=u'Title',
        description=u'The title of the tutorial.',
        required=True)

    path = zope.schema.URI(
        title=u'File Path',
        description=u'Path to the file used for the tutorial',
        required=True)
