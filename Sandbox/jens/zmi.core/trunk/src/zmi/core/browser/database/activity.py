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

        total_loads = 0
        total_stores = 0
        total_connections = 0
        limit = 0
        divs = []
        for div in analysis:
            total_stores = total_stores + div['stores']
            total_loads = total_loads + div['loads']
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
            div.update({'link': 'chart_start=%s&chart_end=%s' % (div['start'], div['end']),
                        'time_offset': time_offset,
                        'store_len': store_len,
                        'load_len': load_len,
                        })
            divs.append(div)


        if analysis:
            start_time = DateTime(divs[0]['start']).aCommonZ()
            end_time = DateTime(divs[-1]['end']).aCommonZ()
        else:
            start_time = ''
            end_time = ''

        res = {'start_time': start_time,
               'end_time': end_time,
               'divs': divs,
               'total_store_count': total_stores,
               'total_load_count': total_loads,
               'total_connections': total_connections,
               }
        return res

    #def getActivityChartData(self):
        #"""test graphing"""
        #return activity