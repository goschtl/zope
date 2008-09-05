##############################################################################
#
# Copyright (c) Zope Corporation and Contributors.
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
import logging, datetime

class CountingHandler(logging.Handler):

    def __init__(self, *args, **kw):
        self.clear()
        logging.Handler.__init__(self, *args, **kw)

    def emit(self, record):
        levelno = record.levelno
        statistics = self._statitistics.get(levelno)
        if statistics is None:
            statistics = [levelno, 0, '']
            self._statitistics[levelno] = statistics

        statistics[1] += 1
        statistics[2] = self.format(record)

    @property
    def statistics(self):
        for levelno in sorted(self._statitistics):
            yield tuple(self._statitistics[levelno])

    def clear(self):
        self._statitistics = {}
        self.start_time = datetime.datetime.utcnow()

def monitor(f, loggername='.', clear=''):
    if loggername == '.':
        logger = logging.getLogger(None)
    else:
        logger = logging.getLogger(loggername)
    for handler in logger.handlers:
        if isinstance(handler, CountingHandler):
            f.write(handler.start_time.isoformat('T')+'\n')
            for record in handler.statistics:
                f.write("%s %s %r\n" % record)
            break
    else:
        raise ValueError("Invalid logger name: "+loggername)
