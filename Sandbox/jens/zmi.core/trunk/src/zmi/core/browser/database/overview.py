##############################################################################
#
# Copyright (c) 2011 Zope Foundation and Contributors.
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
ZODB Overview
"""

import datetime

from Acquisition import aq_inner

from zmi.core.browser.base import ZMIView
from zmi.core.browser.base import Message as _

class View(ZMIView):

    def __call__(self):
        if 'pack' in self.request.form:
            self.handle_pack(data=self.request.form)
            return self.redirect()
        return self.index()

    @property
    def _db(self):
        """Return the database connection"""
        return aq_inner(self.context)._p_jar.db()

    def db_name(self):
        """Return the name of the database"""
        return self._db.getName()

    def db_size(self):
        """Return the size of the database, unformatted if it is a string,
        otherwise in kilobytes or megabytes"""
        size = self._db.getSize()
        if isinstance(size, str):
            return size

        if size >= 1048576.0:
            return '%.1fM' % (size/1048576.0)
        return '%.1fK' % (size/1024.0)

    def handle_pack(self, data):
        """Pack the database by removing revisions older than the number of days
        converted into seconds
        """
        db = self._db
        packtime = datetime.timedelta(days=int(data['days']))
        db.pack(packtime.seconds)
        self.status = _(u'The database was packed')
