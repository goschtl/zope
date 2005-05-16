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
"""Item Vocabulary Views

$Id$
"""
__docformat__ = 'restructuredtext'

from zope.interface import implements, Interface
from zope.schema.vocabulary import VocabularyField
from zope.app.content.folder import Folder

class IDefaultItem(Interface):

    default = VocabularyField(
        title=u"Default Item Key",
        description=u"Key of the default item in the folder.",
        vocabulary="Items")

class DefaultItemFolder(Folder):
    implements(IDefaultItem)

    default = None
    
