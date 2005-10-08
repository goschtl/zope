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

$Id: app.py 7039 2004-10-19 17:27:28Z dhuber $
"""

from persistent import Persistent

from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty

from zope.app.container.btree import BTreeContainer

from kupusupport.sample import IKupuSample, IKupuSampleContainer


class KupuSample(BTreeContainer):
    """A sample kupu content type with different fields.

    >>> content = KupuSample()

    """

    implements(IKupuSample, IKupuSampleContainer)

    title = FieldProperty(IKupuSample['title'])
    description = FieldProperty(IKupuSample['description'])
    body = FieldProperty(IKupuSample['body'])

    def __init__(self):
        super(KupuSample, self).__init__()

    # XXX: has to be removed
    def getHTML(self):
        """Get the body of the object wrapped as HTML by the restx adapter."""
        text = self.body
        name = 'zope.source.rest'
        if text:
            source = zapi.createObject(None, name, text)
            renderer = zapi.getView(source, '', TestRequest())
            return renderer.render()
        else:
            return ""
