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

$Id: folder.py,v 1.2 2004/02/24 16:49:59 philikon Exp $
"""
from zope.interface import implements
from zope.app.browser.container.adding import Adding
from zope.app.folder.interfaces import IFolderAdding

#XXX this is currently not used

class FolderAdding(Adding):
    implements(IFolderAdding)
