##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""

$Id: PasswordWidget.py,v 1.2 2002/06/10 23:27:49 jim Exp $
"""

from TextWidget import TextWidget


class PasswordWidget(TextWidget):
    
    def render(self, REQUEST=None):
        """Render password input field.
        """
        display_maxwidth = field.get_value('display_maxwidth') or 0
        if display_maxwidth > 0:
            return render_element("input",
                                  type="password",
                                  name=key,
                                  css_class=field.get_value('css_class'),
                                  value=value,
                                  size=field.get_value('display_width'),
                                  maxlength=display_maxwidth,
                                  extra=field.get_value('extra'))
        else:
            return render_element("input",
                                  type="password",
                                  name=key,
                                  css_class=field.get_value('css_class'),
                                  value=value,
                                  size=field.get_value('display_width'),
                                  extra=field.get_value('extra'))
