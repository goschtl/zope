##############################################################################
#
# Copyright (c) 2005, 2006 Zope Corporation and Contributors.
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

"""Result reporting resource for zc.selenium.
"""

import sys
import zc.selenium.selenium
import zope.app.pagetemplate


class Results(object):
    """Transports test results from the browser to the selenium test runner"""

    template = zope.app.pagetemplate.ViewPageTemplateFile('results.pt')

    def __call__(self):
        if hasattr(zc.selenium.selenium, 'messages'):
            zc.selenium.selenium.messages.put(self.request)
        return self.template(self)
