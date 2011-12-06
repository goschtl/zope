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

    start_time = 'start_time'
    end_time = 'end_time'

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

    def getActivityChartData(self, segment_height=200, REQUEST=None):
        """Returns information for generating an activity chart.
        Default height is 200 pixels
        """
        segment_height = int(segment_height)
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

        segment_time = 0
        start_time = ''
        end_time = ''
        if analysis is not None:
            segment_time = analysis[0]['end'] - analysis[0]['start']
            start_time = time.strftime("%a, %d %b %Y %H:%M:%S %Z",
                                       time.gmtime(analysis[0]['start']))
            end_time = time.strftime("%a, %d %b %Y %H:%M:%S %Z",
                                     time.gmtime(analysis[-1]['end']))

        divs = []

        total_stores, total_loads, total_connections = (
            sum(d[k] for d in analysis)
            for k in ('stores', 'loads', 'connections')
        )

        limit = max(((d['stores'] + d['loads']) for d in analysis))

        def calculated():
            """Utility function to calculate bar heights and time offsets"""
            now = analysis[-1]['end']
            for div in analysis:
                stores = div['stores']
                loads = div['loads']
                store_len = 0
                load_len = 0

                if stores > 0:
                    store_len = max((segment_height * stores / limit), 1)
                if loads > 0:
                    load_len = max((segment_height * loads / limit), 1)

                offset = div['end'] - now  # Offset from most recent measurement.
                if segment_time >= 3600:
                    # Show hours.
                    time_offset = '%dh' % (offset / 3600)
                elif segment_time >= 60:
                    # Show minutes.
                    time_offset = '%dm' % (offset / 60)
                elif segment_time >= 1:
                    # Show seconds.
                    time_offset = '%ds' % offset
                else:
                    # Show fractions.
                    time_offset = '%.2fs' % offset

                div.update({'link': 'chart_start=%s&chart_end=%s' % (div['start'], div['end']),
                            'time_offset': time_offset,
                            'store_len': store_len,
                            'load_len': load_len,
                            })
                yield div

        return {'start_time': start_time,
               'end_time': end_time,
               'divs': calculated,
               'total_store_count': total_stores,
               'total_load_count': total_loads,
               'total_connections': total_connections,
               }
