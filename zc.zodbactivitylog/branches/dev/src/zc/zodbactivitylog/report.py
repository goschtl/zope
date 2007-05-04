##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
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
"""Simple report for zodb activity log
"""

import datetime, sys

def parsedt(s):
    date, time = s.split('T')
    return datetime.datetime(*(
        map(int, date.split('-')) 
        +
        map(int, time.split(':'))         
        ))

def main(args=None):
    if args is None:
        args = sys.argv[1:]

    try:
        [file, deltat] = args
        deltat = int(deltat)
    except ValueError:
        try:
            [file] = args
            deltat = 5
        except ValueError:
            print 'usage: %s filename [minutes]' % sys.argv[0]
            sys.exit(1)

    start = None

    last = None
    sum_reads = sum_writes = 0
    for line in open(file):
        dt, reads, writes = line.split()[:3]
        date, time = dt.split('T')
        h, m = time.split(':')[:2]
        m = (int(m) // deltat) * deltat
        key = date, h, m
        if key != last:
            if last is not None:
                print "%sT%s:%.2d" % last, sum_reads, sum_writes
                sum_reads = sum_writes = 0
            last = key
        sum_reads += int(reads)
        sum_writes += int(writes)

    if key and (sum_reads or sum_writes):
        print "%sT%s:%.2d" % last, sum_reads, sum_writes
        
                
        
    
