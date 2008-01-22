##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Log formatter that enhances tracebacks with extra information.

$Id$
"""

import logging
import cStringIO
from zope.exceptions.exceptionformatter import print_exception

class Formatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, as_html=0,):
        logging.Formatter.__init__(self, fmt=fmt, datefmt=datefmt)
        self.as_html = as_html

    def format(self, record):
        record.message = record.getMessage()
        if self._fmt.find("%(asctime)") >= 0:
            record.asctime = self.formatTime(record, self.datefmt)
        cdict = record.__dict__.copy()
        lines = []
        for line in record.message.splitlines():
            cdict['message'] = line
            lines.append(self._fmt % cdict)
        s = '\n'.join(lines)
        if record.exc_info:
            # Cache the traceback text to avoid converting it multiple times
            # (it's constant anyway)
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info, record=record)
        if record.exc_text:
            s = record.exc_text
        else:
            cdict = record.__dict__.copy()
            lines = []
            for line in record.message.splitlines():
                cdict['message'] = line
                lines.append(self._fmt % cdict)
            s = '\n'.join(lines)
        return s

    def formatException(self, ei, record=None):
        """Format and return the specified exception information as a string.

        Uses zope.exceptions.exceptionformatter to generate the traceback.
        """
        sio = cStringIO.StringIO()
        if record:
            format = (self._fmt, record)
        else:
            format = None

        print_exception(
            ei[0],
            ei[1],
            ei[2],
            file=sio,
            as_html=self.as_html,
            with_filenames=True,
            format=format)
        s = sio.getvalue()
        if s.endswith("\n"):
            s = s[:-1]
        return s
