#############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

"""Simple column indices
$Id$
"""

from Products.PluginIndexes import PluggableIndex
from Products.PluginIndexes.common.UnIndex import UnIndex

from Globals import DTMLFile

class FieldIndex(UnIndex):
    """Field Indexes"""

    __implements__ = (PluggableIndex.UniqueValueIndex,
                      PluggableIndex.SortIndex)

    meta_type="FieldIndex"

    manage_options= (
        {'label': 'Settings',
         'action': 'manage_main',
         'help': ('FieldIndex','FieldIndex_Settings.stx')},
        {'label': 'Browse',
         'action': 'manage_browse',
         'help': ('FieldIndex','FieldIndex_Settings.stx')},
    )

    query_options = ["query","range"]

    index_html = DTMLFile('dtml/index', globals())

    manage_workspace = DTMLFile('dtml/manageFieldIndex', globals())
    manage_browse = DTMLFile('../dtml/browseIndex', globals())


manage_addFieldIndexForm = DTMLFile('dtml/addFieldIndex', globals())

def manage_addFieldIndex(self, id, extra=None,
                REQUEST=None, RESPONSE=None, URL3=None):
    """Add a field index"""
    return self.manage_addIndex(id, 'FieldIndex', extra=extra, \
             REQUEST=REQUEST, RESPONSE=RESPONSE, URL1=URL3)
