##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Configuration Browser Views

XXX longer description goes here.

$Id: configurationstatuswidget.py,v 1.2 2002/12/25 14:12:36 jim Exp $
"""
__metaclass__ = type

from zope.app.browser.form.widget import BrowserWidget
from zope.app.interfaces.services.configuration \
     import Active, Registered, Unregistered

class ConfigurationStatusWidget(BrowserWidget):

    def __call__(self):
        checked = self._showData() or Unregistered
        result = [
            ('<label><input type="radio" name="%s" value="%s"%s>&nbsp;%s</label>'
             % (self.name, v, (v == checked and ' checked' or ''), v)
             )
            for v in (Unregistered, Registered, Active)
            ]
        return ' '.join(result)
