##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Datetime widget

$Id$
"""

from zope.app.datetimeutils import parseDatetimetz
from zope.app.datetimeutils import DateTimeError
from zope.app.form.browser import textwidgets

template = """
%(widget_html)s
<input type="button" value="..." id="%(name)s_trigger">
<script type="text/javascript">
  Calendar.setup(
    {
      inputField: "%(name)s", // ID of the input field
      ifFormat: "%(datetime_format)s", // the date format
      button: "%(name)s_trigger", // ID of the button
      showsTime: %(showsTime)s
    }
  );
</script>
"""


class DatetimeBase(object):

    def __call__(self):
        widget_html = super(DatetimeBase, self).__call__()
        return template % {"widget_html": widget_html,
                           "name": self.name,
                           "showsTime": self._showsTime,
                           "datetime_format": self._format}


class DatetimeWidget(DatetimeBase, textwidgets.DatetimeWidget):
    """Datetime entry widget."""

    _format = '%Y-%m-%d %H:%M:%S'
    _showsTime = "true"


class DateWidget(DatetimeBase, textwidgets.DateWidget):
    """Date entry widget."""

    _format = '%Y-%m-%d'
    _showsTime = "false"
