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

$Id: app.py 6924 2004-10-14 09:57:19Z rineichen $
"""

from zope.interface import implements

from zorg.kupusupport.interfaces import IKupuPolicy
from zorg.kupusupport.sample import IKupuSample


class KupuSamplePolicy(object):
    """A sample kupu content type with different fields.

    The body attribute stores kupu relevant data::

    >>> from zorg.kupusupport.sample.app import KupuSample
    >>> content = KupuSample()
    >>> content.body = u'Initial value'

    The update method changes for example the body attribute of the content::

    >>> updatepolicy = KupuSamplePolicy(content)
    >>> kupu = '...<body>Updated value</body>...'
    >>> updatepolicy.update(kupu)

    The display method shows the relevant content::

    >>> updatepolicy.display() is content.body
    True
    >>> updatepolicy.display()
    u'Updated value'

    """

    implements(IKupuPolicy)

    __used_for__ = IKupuSample

    def __init__(self, context):
        self.context = context

    def update(self, kupu=None):
        if kupu:
            body_start = kupu.find('<body>') + len('<body>')
            body_end = kupu.rfind('</body>')
            body = kupu[body_start:body_end]
            self.context.body = unicode(body)


    def display(self):
        return self.context.body
