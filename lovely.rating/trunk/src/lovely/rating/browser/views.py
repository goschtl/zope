##############################################################################
#
# Copyright (c) 2006 Lovely Systems and Contributors.
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
"""Rating test setup

$Id$
"""

from zope.publisher.browser import BrowserPage
from zope.app.pagetemplate import ViewPageTemplateFile

class RatingView(BrowserPage):

    template = ViewPageTemplateFile('rating.pt')

    def update(self):
        pass

    def __call__(self):
        self.update()
        return self.template()


class RatingForm(BrowserPage):

    template = ViewPageTemplateFile('rating_form.pt')

    def update(self):
        rate = self.request.get('rateContent', None)
        if rate is not None:
            # TODO: implement rate content here

    def __call__(self):
        self.update()
        return self.template()
