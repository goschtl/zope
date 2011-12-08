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
import unittest


seconds_activity = [
    {'end':1, 'connections':15, 'start':0,'stores':5, 'loads':10},
    {'end':2, 'connections':25, 'start':1,'stores':15,'loads':10}
]

minutes_activity = [
    {'end':3600, 'connections':15, 'start':0, 'stores':250, 'loads':1000},
    {'end':3601, 'connections':15, 'start':86400, 'stores':500, 'loads':2000}
]

hours_activity = [
    {'end':86400, 'connections':15, 'start':0, 'stores':250,' loads':1000},
    {'end':172800, 'connections':15, 'start':86400, 'stores':500, 'loads':2000}
]

fractional_activity = [
    {'end':0.5, 'connections':15, 'start':0, 'stores':250, 'loads':1000},
    {'end':1, 'connections':15, 'start':0.5, 'stores':500, 'loads':2000}
]

class DummyDatabaseConnection:

    def __init__(self):
        self.am = DummyActivityMonitor()

    def db(self):
        return self

    def getActivityMonitor(self):
        return getattr(self, 'am', None)


class DummyDatabaseObject:

    def __init__(self):
        self._p_jar = DummyDatabaseConnection()


class DummyActivityMonitor:

    def __init__(self, activity=seconds_activity):
        self.activity = activity[:]

    def getHistoryLength(self):
        return 3600

    def getActivityAnalysis(self, start=None, end=None, divisions=None):
        return self.activity


class Tests(unittest.TestCase):

    def _getTargetClass(self):
        from zmi.core.browser.database.activity import View
        return View

    def _makeOne(self):
        root = DummyDatabaseObject()
        view = self._getTargetClass()
        return view(root, {})

    def test_no_activity_monitor(self):
        view = self._makeOne()
        delattr(view._db, 'am')

        history = view.getHistoryLength()
        self.assertEqual(history, 0)

        am = view._getActivityMonitor()
        self.assertIsNone(am)

        data = view.getActivityChartData()
        self.assertIsNone(data)


    def test_getHistoryLength(self):
        view = self._makeOne()
        self.assertEqual(view.getHistoryLength(), 3600)

    def test_timings_seconds(self):
        view = self._makeOne()
        data = view._get_timings(seconds_activity)
        expected = ('Thu, 01 Jan 1970 00:00:00 CET',
                    'Thu, 01 Jan 1970 00:00:02 CET',
                    1)
        self.assertEqual(data, expected)

    def test_timings_minutes(self):
        view = self._makeOne()
        data = view._get_timings(minutes_activity)
        expected = ('Thu, 01 Jan 1970 00:00:00 CET',
                    'Thu, 01 Jan 1970 01:00:01 CET',
                    3600)
        self.assertEqual(data, expected)

    def test_timings_hours(self):
        view = self._makeOne()
        data = view._get_timings(hours_activity)
        expected = ('Thu, 01 Jan 1970 00:00:00 CET',
                    'Sat, 03 Jan 1970 00:00:00 CET',
                    86400)
        self.assertEqual(data, expected)

    def test_timings_fractions(self):
        view = self._makeOne()
        data = view._get_timings(fractional_activity)
        expected = ('Thu, 01 Jan 1970 00:00:00 CET',
                    'Thu, 01 Jan 1970 00:00:01 CET',
                    0.5)
        self.assertEqual(data, expected)

    def test_chart_data(self):
        view = self._makeOne()
        start, end, interval = view._get_timings(seconds_activity)
        data = view._chart_data(interval, 200, seconds_activity).next()
        expected = {'store_len': 40, 'end': 1, 'load_len': 80,
                    'connections': 15, 'start': 0, 'link':
                    'chart_start=0&chart_end=1', 'stores': 5, 'loads': 10,
                    'time_offset': '-1s'}
        self.assertEqual(data, expected)

    def test_getActivityChartData(self):
        view = self._makeOne()
        data = view.getActivityChartData()
        expected =  {'start_time': 'Thu, 01 Jan 1970 00:00:00 CET',
                     'total_load_count': 20,
                     'end_time': 'Thu, 01 Jan 1970 00:00:02 CET',
                     'total_store_count': 20, 'total_connections': 40,}
        for k in expected:
            self.assertEqual(data[k], expected[k])

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(Tests),
        ))