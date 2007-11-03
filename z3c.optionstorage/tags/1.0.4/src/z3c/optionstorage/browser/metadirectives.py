##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
from zope.app.publisher.browser.metadirectives import IViewDirective
from zope.configuration.fields import MessageID
from zope.interface import Interface
from zope.schema import TextLine


class IOptionStorageDirective(IViewDirective):
    """
    The manageableVocabularies directive is used to create a
    vocabulary editing view for a given interface.
    """

class IOptionStorageOptionsSubdirective(Interface):

    name = TextLine(
                   title=u"Key of option dictionary in storage",
                   required=True,
                   )

    topic = MessageID(
                   title=u"Topic of option dictionary in storage",
                   required=True,
                   )

