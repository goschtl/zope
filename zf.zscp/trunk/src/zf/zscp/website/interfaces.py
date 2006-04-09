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
"""ZSCP Web Site Interfaces

$Id$
"""
__docformat__ = "reStructuredText"
import os.path
import zope.schema
from zope.app import folder

from zf.zscp.i18n import MessageFactory as _
from zope.app.container.constraints import containers
from zope.app.container.constraints import contains


def isDirectory(path):
    if path:
        return os.path.isdir(path)
    else:
        return True


class IZSCPSite(folder.interfaces.IFolder):
    """The root object for the ZSCP site.

    The site mainly contains ZSCP repository objects.
    """

    containers(folder.interfaces.IFolder)

    contains('zf.zscp.interfaces.IZSCPRepository')

    certificationDir = zope.schema.TextLine(title=_(u'Path'),
        description=_(u'Path to the directory.'),
        required=False,
        constraint=isDirectory,
        max_length=255)
