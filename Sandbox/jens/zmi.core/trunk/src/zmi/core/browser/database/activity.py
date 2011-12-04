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
ZODB Activity
"""

from Acquisition import aq_inner
from DateTime import DateTime

class View(object):

    # dummy variables for bootstrapping view
    getHistoryLength = 1
    start_time = "start_time"
    end_time = "end_time"
    divs = ()
    connections = "connections"
    trans_len = "trans_len"
    store_len = "store_len"
    load_len = "load_len"
    total_store_count = "total_store_count"

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        return self.index()

    @property
    def _db(self):
        """Return the database connection"""
        return aq_inner(self.context)._p_jar.db()

    def _getActivityMonitor(self):
        if not hasattr(self._db, 'getActivityMonitor'):
            return None
        am = self._db.getActivityMonitor()
        if am is None:
            return None
        return am

    def getHistoryLength(self):
        am = self._getActivityMonitor()
        if am is None:
            return 0
        return am.getHistoryLength()

    def getActivityChartData(self, segment_height=200, REQUEST=None):
        """Returns information for generating an activity chart.
        Default height is 200 pixels
        """
        am = self._getActivityMonitor()
        if am is None:
            return None

        if REQUEST is not None:
            start = float(REQUEST.get('chart_start', 0))
            end = float(REQUEST.get('chart_end', 0))
            divisions = int(REQUEST.get('chart_divisions', 10))
            analysis = am.getActivityAnalysis(start, end, divisions)
        else:
            analysis = am.getActivityAnalysis()

        total_load_count = 0
        total_store_count = 0
        total_connections = 0
        limit = 0
        divs = []
        for div in analysis:
            total_store_count = total_store_count + div['stores']
            total_load_count = total_load_count + div['loads']
            total_connections = total_connections + div['connections']
            sum = div['stores'] + div['loads']
            if sum > limit:
                limit = sum

        if analysis:
            segment_time = analysis[0]['end'] - analysis[0]['start']
        else:
            segment_time = 0

        for div in analysis:
            stores = div['stores']
            if stores > 0:
                store_len = max(int(segment_height * stores / limit), 1)
            else:
                store_len = 0
            loads = div['loads']
            if loads > 0:
                load_len = max(int(segment_height * loads / limit), 1)
            else:
                load_len = 0

            t = div['end'] - analysis[-1]['end']  # Show negative numbers.
            if segment_time >= 3600:
                # Show hours.
                time_offset = '%dh' % (t / 3600)
            elif segment_time >= 60:
                # Show minutes.
                time_offset = '%dm' % (t / 60)
            elif segment_time >= 1:
                # Show seconds.
                time_offset = '%ds' % t
            else:
                # Show fractions.
                time_offset = '%.2fs' % t
            divs.append({
                'store_len': store_len,
                'load_len': load_len,
                'trans_len': max(segment_height - store_len - load_len, 0),
                'store_count': div['stores'],
                'load_count': div['loads'],
                'connections': div['connections'],
                'start': div['start'],
                'end': div['end'],
                'time_offset': time_offset,
            })

        if analysis:
            start_time = DateTime(divs[0]['start']).aCommonZ()
            end_time = DateTime(divs[-1]['end']).aCommonZ()
        else:
            start_time = ''
            end_time = ''

        res = {'start_time': start_time,
               'end_time': end_time,
               'divs': divs,
               'total_store_count': total_store_count,
               'total_load_count': total_load_count,
               'total_connections': total_connections,
               }
        return res

