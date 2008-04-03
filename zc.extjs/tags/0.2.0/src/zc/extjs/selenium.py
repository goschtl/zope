##############################################################################
#
# Copyright (c) Zope Corporation. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Visible Source
# License, Version 1.0 (ZVSL).  A copy of the ZVSL should accompany this
# distribution.
#
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

import zc.selenium.pytest
class SeleniumTests(zc.selenium.pytest.Test):

    def testCalculator(self):
        s = self.selenium
        s.open('/calculator.html?login')
        s.waitForText('value', '0')
        s.type('input', '2')
        s.click('add-button')
        s.waitForText('value', '2')
        s.click('add-button')
        s.waitForText('value', '4')
        s.type('input', '3')
        s.click('subtract-button')
        s.waitForText('value', '1')
      
