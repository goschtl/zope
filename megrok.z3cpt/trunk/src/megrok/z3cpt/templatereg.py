##############################################################################
#
# Copyright (c) 2008 Zope Corporation and Contributors.
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

from zope.interface import implements
from grokcore.view.interfaces import ITemplateFileFactory
from megrok.z3cpt import PageTemplate
import grokcore.component


class PageTemplateFileFactory(grokcore.component.GlobalUtility):
    implements(ITemplateFileFactory)
    grokcore.component.name('zpt')

    def __call__(self, filename, _prefix=None):
        return PageTemplate(filename=filename, _prefix=_prefix)
