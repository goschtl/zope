##############################################################################
#
# Copyright (c) 2003-2004 Kupu Contributors. All rights reserved.
#
# This software is distributed under the terms of the Kupu
# License. See LICENSE.txt for license text. For a list of Kupu
# Contributors see CREDITS.txt.
#
##############################################################################
"""Zope3 isar sprint sample integration

$Id: interfaces.py 7039 2004-10-19 17:27:28Z dhuber $
"""

from zope.interface import Interface
from zope.schema import SourceText
from zope.schema import TextLine
from zope.i18nmessageid import MessageIDFactory

from zope.app.container.constraints import ItemTypePrecondition
from zope.app.container.interfaces import IContainer
from zope.app.file.interfaces import IImage
from zope.app.folder.interfaces import IFolder


_ = MessageIDFactory("kupu")
        

class IKupuSample(Interface):
    """Sample kupu content implementation."""

    title = TextLine(
        title=_(u"Title"),
        description=_(u"Title of the content."),
        default=u"",
        required=True)

    description = TextLine(
        title=_(u"Description"),
        description=_(u"Description of the content."),
        default=u"",
        required=True)

    body = SourceText(
        title=_(u"Kupu Body text"),
        description=_(u"Kupu renderable source text of the body."),
        default=u"",
        required=True)


class IKupuSampleContainer(IContainer):
    """Sample kupu content cotains its own images and other kupu samples"""

    def __setitem__(name, object): 
        """Add Images."""
    
    __setitem__.precondition = ItemTypePrecondition(IImage, IKupuSample)
