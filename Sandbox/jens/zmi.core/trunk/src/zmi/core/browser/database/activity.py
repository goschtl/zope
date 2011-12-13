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

import time

from Acquisition import aq_inner

#dummy data

activity = {'start_time': 'Dec 4, 2011 6:15 pm GMT+1', 'total_load_count': 0, 'end_time': 'Dec 4, 2011 7:15 pm GMT+1',
            'divs': [{'stores': 0, 'connections': 0, 'store_len': 50, 'end': 1323019271.8497, 'start': 1323018911.8497, 'load_len': 100, 'loads': 0, 'time_offset': '-54m', 'link':''},
                     {'stores': 0, 'connections': 0, 'store_len': 40, 'end': 1323019631.8497, 'start': 1323019271.8497, 'load_len': 100, 'loads': 0, 'time_offset': '-48m', 'link':''},
                     {'stores': 0, 'connections': 0, 'store_len': 30, 'end': 1323019991.8497, 'start': 1323019631.8497, 'load_len': 100, 'loads': 0, 'time_offset': '-42m', 'link':''},
                     {'stores': 0, 'connections': 0, 'store_len': 20, 'end': 1323020351.8497, 'start': 1323019991.8497, 'load_len': 110, 'loads': 0, 'time_offset': '-36m', 'link':''},
                     {'stores': 0, 'connections': 0, 'store_len': 10, 'end': 1323020711.8497, 'start': 1323020351.8497, 'load_len': 120, 'loads': 0, 'time_offset': '-30m', 'link':''},
                     {'stores': 0, 'connections': 0, 'store_len': 0,  'end': 1323021071.8497, 'start': 1323020711.8497, 'load_len': 130, 'loads': 0, 'time_offset': '-24m', 'link':''},
                     {'stores': 0, 'connections': 0, 'store_len': 100,'end': 1323021431.8497, 'start': 1323021071.8497, 'load_len': 100, 'loads': 0, 'time_offset': '-18m', 'link':''},
                     {'stores': 0, 'connections': 0, 'store_len': 110,'end': 1323021791.8497, 'start': 1323021431.8497, 'load_len': 80, 'loads': 0, 'time_offset': '-12m', 'link':''},
                     {'stores': 0, 'connections': 0, 'store_len': 10, 'end': 1323022151.8497, 'start': 1323021791.8497, 'load_len': 20, 'loads': 0, 'time_offset': '-6m', 'link':''},
                     {'stores': 0, 'connections': 0, 'store_len': 40, 'end': 1323022511.8497, 'start': 1323022151.8497, 'load_len': 30, 'loads': 0, 'time_offset': '0m', 'link':''}],
            'total_store_count': 0, 'total_connections': 0}


class View(object):

    start_time = ""
    end_time = ""
    segment_height = 200
    time_unit = 1
    time_fmt = "%.2fs" # microseconds

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
            return
        am = self._db.getActivityMonitor()
        return am

    def getHistoryLength(self):
        am = self._getActivityMonitor()
        if am is None:
            return 0
        return am.getHistoryLength()

    def _get_timings(self, analysis):
        """Calculate time format and start and end times"""
        if analysis is not None:
            segment_time = analysis[0]['end'] - analysis[0]['start']
            self.start_time = time.strftime("%a, %d %b %Y %H:%M:%S %Z",
                                       time.gmtime(analysis[0]['start']))
            self.end_time = time.strftime("%a, %d %b %Y %H:%M:%S %Z",
                                     time.gmtime(analysis[-1]['end']))
        if segment_time >= 3600: # hours
            self.time_unit = 3600
            self.time_fmt = "%dh"
        elif segment_time >= 60: # minutes
            self.time_unit = 60
            self.time_fmt = "%dm"
        elif segment_time >= 1: # seconds
            self.time_fmt = "%ds"

    def _chart_data(self, analysis):
        """Utility function to calculate bar heights and time offsets"""

        limit = max(((d['stores'] + d['loads']) for d in analysis))

        now = analysis[-1]['end']
        for div in analysis:
            stores = div['stores']
            loads = div['loads']
            store_len = 0
            load_len = 0

            if stores > 0:
                store_len = max((self.segment_height * stores / limit), 1)
            if loads > 0:
                load_len = max((self.segment_height * loads / limit), 1)

            offset = div['end'] - now  # Offset from most recent measurement.
            time_offset = self.time_fmt % (offset / self.time_unit)

            div.update({'link': 'chart_start=%s&chart_end=%s' % (div['start'], div['end']),
                        'time_offset': time_offset,
                        'store_len': store_len,
                        'load_len': load_len,
                        })
            yield div

    def getActivityChartData(self, segment_height=200, REQUEST=None):
        """Returns information for generating an activity chart.
        Default height is 200 pixels
        """
        self.segment_height = int(segment_height)
        am = self._getActivityMonitor()
        if am is None:
            return

        if REQUEST is not None:
            start = float(REQUEST.get('chart_start', 0))
            end = float(REQUEST.get('chart_end', 0))
            divisions = int(REQUEST.get('chart_divisions', 10))
            analysis = am.getActivityAnalysis(start, end, divisions)
        else:
            analysis = am.getActivityAnalysis()

        self._get_timings(analysis)

        total_stores, total_loads, total_connections = (
            sum(d[k] for d in analysis)
            for k in ('stores', 'loads', 'connections')
        )

        return {'start_time': self.start_time,
               'end_time': self.end_time,
               'divs': self._chart_data(analysis),
               'total_store_count': total_stores,
               'total_load_count': total_loads,
               'total_connections': total_connections,
               }
