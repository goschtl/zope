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
"""PageletChooser Demo

$Id$
"""
__docformat__ = 'restructuredtext'

from zope.interface import Interface

from zope.schema import Text
from zope.schema import TextLine
from zope.schema import Choice

from zope.i18n import MessageIDFactory
_ = MessageIDFactory('zope')

from zope.app.pageletchooser.interfaces import IChooseablePagelets



class IPageletChooserContent(Interface):
    """A sample content type for to test pagelet chooser."""

    title = TextLine(
        title=_(u"Title"),
        description=_(u"Title of the sample"),
        default=u"",
        required=False)
    
    description = Text(
        title=_(u"Description"),
        description=_(u"Description of the sample"),
        default=u"",
        required=False)



class IFirstLevelPagelets(IChooseablePagelets):
    """Slot for first level pagelets.
    
    IChooseablePagelets inherited slots will use the MacroChooser
    collector for to collect pagelet names.

    The Choice field is useing the vocabulary 'firstlevelmacronames' for 
    to lookup the first level macro names and render a select box in the 
    'edit.html' view.
    
    """

    firstlevel = Choice(
                        title = _(u"First level pagelet macro name."),
                        description = _(u"Select the first level pagelet macro name."),
                        default = 'notfoundmacro',
                        required = True,
                        vocabulary = "firstlevelmacronames",
                        )
