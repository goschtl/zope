##############################################################################
#
# Copyright (c) 2004-2008 Zope Corporation and Contributors.
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
"""Profiler support for the test runner

$Id: __init__.py 86218 2008-05-03 14:17:26Z ctheune $
"""

import glob

available_profilers = {}


try:
    import cProfile
    import pstats
except ImportError:
    pass
else:
    class CProfiler(object):
        """cProfiler"""
        def __init__(self, filepath):
            self.filepath = filepath
            self.profiler = cProfile.Profile()
            self.enable = self.profiler.enable
            self.disable = self.profiler.disable

        def finish(self):
            self.profiler.dump_stats(self.filepath)

        def loadStats(self, prof_glob):
            stats = None
            for file_name in glob.glob(prof_glob):
                if stats is None:
                    stats = pstats.Stats(file_name)
                else:
                    stats.add(file_name)
            return stats

    available_profilers['cProfile'] = CProfiler


# some Linux distributions don't include the profiler, which hotshot uses
try:
    import hotshot
    import hotshot.stats
except ImportError:
    pass
else:
    class HotshotProfiler(object):
        """hotshot interface"""

        def __init__(self, filepath):
            self.profiler = hotshot.Profile(filepath)
            self.enable = self.profiler.start
            self.disable = self.profiler.stop

        def finish(self):
            self.profiler.close()

        def loadStats(self, prof_glob):
            stats = None
            for file_name in glob.glob(prof_glob):
                loaded = hotshot.stats.load(file_name)
                if stats is None:
                    stats = loaded
                else:
                    stats.add(loaded)
            return stats

    available_profilers['hotshot'] = HotshotProfiler
