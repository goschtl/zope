##############################################################################
#
# Copyright (c) 2005, 2006 Zope Corporation. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Visible Source
# License, Version 1.0 (ZVSL).  A copy of the ZVSL should accompany this
# distribution.
#
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Result reporting resource for zc.selenium.

"""

import sys

import zope.app.pagetemplate

import zc.selenium.resource

class Results(zc.selenium.resource.ResourceBase):

    template = zope.app.pagetemplate.ViewPageTemplateFile('results.pt')

    def POST(self):
        # get the queue used to communicate with the test thread, this will
        # fail horribly if not running in "Selenium test" mode
        messages = sys.modules['__main__'].messages
        messages.put(self.request)
        return self.template(self)
