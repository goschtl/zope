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
"""Folder-specific view classes

$Id: folder.py,v 1.3 2004/03/14 02:17:04 srichter Exp $
"""
from zope.interface import implements
from zope.app.container.browser.adding import Adding
from zope.app.folder.interfaces import IFolderAdding

#XXX this is currently not used

class FolderAdding(Adding):
    implements(IFolderAdding)
