##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""

$Id: testing.py 39651 2005-10-26 18:36:17Z oestermeier $
"""

from string import Template

import zope.component
from zope.interface import implements
import zope.app.testing.placelesssetup
from zope.app import zapi

from zorg.edition.interfaces import IUUIDGenerator
from zorg.edition.uuid import UUIDGenerator

from zorg.live.page.page import LivePage
from zorg.live.page.interfaces import IClientEventFactory
from zorg.live.page import event


class TestUUIDGenerator(object) :
    """ A generator that produces always the same sequence of uuids for test
        purposes.
    """
    implements(IUUIDGenerator)
    
    def __init__(self) :
        self.count = 0
        
    def __call__(self) :
        self.count += 1
        return "uuid%s" % self.count
    
def livePageSetUp(test=None) :
    zope.component.provideUtility(TestUUIDGenerator(), IUUIDGenerator)

    zope.component.provideUtility(event.Append, IClientEventFactory,
                                                               name="append")
    zope.component.provideUtility(event.Update, IClientEventFactory,
                                                               name="update")

class PlacelessSetup(zope.app.testing.placelesssetup.PlacelessSetup):

    def setUp(self, doctesttest=None):
        super(PlacelessSetup, self).setUp(doctesttest)
        
        # zope.app.annotations
        from zope.app.annotation.interfaces import IAnnotations
        from zope.app.annotation.interfaces import IAttributeAnnotatable
        from zope.app.annotation.attribute import AttributeAnnotations

        zope.component.provideAdapter(AttributeAnnotations,
            [IAttributeAnnotatable], IAnnotations)

        livePageSetUp()
        
    def tearDown(self, test=None):
        super(PlacelessSetup, self).tearDown()

placelesssetup = PlacelessSetup()


class TestLivePage(LivePage) :
    
    def render(self) :
        """ A test method that calls the livepage. 
            
            The method must call self.nextClientId to
            ensure that a unique key is generated.
            
        """
        
        url = zapi.absoluteURL(self.context, self.request) 
        url += "/++resource++zorgajax"

        template = Template("""<html>
    <head>
        <script src="$url/prototype.js" type="text/javascript"></script>
        <script type="text/javascript">var livePageUUID = '$id';</script>
        <script src="$url/livepage.js" type="text/javascript"></script>
    </head>
    <body onload="startClient()">
    <p>Input some text.</p>
    <input onchange="sendEvent('append', 'target', this.value)" type="text" />
    <p id="target">Text goes here:</p>
    </body>
</html>""")      
                                                
        return template.substitute(id=self.nextClientId(), url=url)
        