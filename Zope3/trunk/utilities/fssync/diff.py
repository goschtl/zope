##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

import os, commands, calendar

from common import getObjectDataTempfile

def getdiff(targetfile, objpath, dbpath, siteconfpath, diffoption=None):
    """Returns the difference between two files

    Gets the diff between :
        -- Current in Sandbox and Original of last sync
        -- Current in Sandbox and Current in ZODB
        -- Current in ZODB and Original of last sync.
    """
    temp_file = ''
    objectpath = ''
    modification_date = None
    zodbtargetfile = targetfile
    if not os.path.isabs(targetfile):
        targetfile=os.path.join(os.path.abspath(os.curdir), targetfile)
    if not os.path.exists(targetfile):
        return ("sync [diff aborted] : Target file does not exist --- %s" %
                targetfile)
    if os.path.isdir(targetfile):
        return ("sync [diff aborted] : "
                "Target file found to be a directory --- %s" %
                targetfile)
    if not os.path.exists(
        os.path.join(os.path.abspath(os.path.dirname(targetfile)), '@@Zope')):
        return 'sync [diff aborted] : @@Zope administrative folder not found'

    if os.path.basename(targetfile).find(' ') >= 0:
        targetfile = os.path.join(os.path.dirname(targetfile),
                                  "'"+os.path.basename(targetfile)+"'")

    if diffoption == '-1':
        from_file = os.path.join(os.path.dirname(targetfile),
                                 '@@Zope', 'Original')
        to_file = targetfile
    elif diffoption == '-2':
        tup = getObjectDataTempfile(zodbtargetfile, objpath, dbpath,
                                    siteconfpath)
        temp_file, objectpath, modification_date = tup
        from_file = targetfile
        to_file = temp_file
    elif diffoption == '-3':
        tup = getObjectDataTempfile(zodbtargetfile, objpath, dbpath,
                                    siteconfpath)
        temp_file, objectpath, modification_date = tup
        from_file = os.path.join(os.path.dirname(targetfile),
                                 '@@Zope', 'Original',
                                 os.path.basename(targetfile))
        to_file = temp_file

    diff_cmd ="diff -a -b -B -c %s %s" % (from_file, to_file)
    diff_res = commands.getoutput(diff_cmd)
    diff_res = setOutput(diff_res, temp_file, objectpath, modification_date)
    print diff_res

    if temp_file:
        os.remove(temp_file)

    return None

weekdays = {0: 'Mon', 1: 'Tue', 2: 'Wed', 3: 'Thu',
            4: 'Fri', 5: 'Sat', 6: 'Sun'}
months = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
          7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}

def getDiffDate(strdt):
    """Returns date in Day Mon DD hh:mm:ss YYYY format.

    Input is either empty or of the form YYYY-MM-DDThh:mm:ss[.uuuuuu]
    (T is a literal T).
    """
    if not strdt:
        return ""
    strdt = str(strdt)
    date, fulltime = strdt.split('T')
    yyyy, mm, dd = date.split('-')
    time = filltime.split('.')[0]
    day = weekdays[calendar.weekday(int(yyyy), int(mm), int(dd))]
    return "%s %s %s %s %s" % (day, months[int(mm)], dd, time, yyyy)

def setOutput(diff_res, temp_file, objectpath, modification_date):
    """Sets the diff output replacing it with original object
    path and modification datetime.
    """
    changed_line = ''
    modification_date = getDiffDate(modification_date)
    if temp_file:
        for line in diff_res.split('\n'):
            if line.find(temp_file) >= 0:
                changed_line = line
                break
        if changed_line:
            newline = changed_line[:changed_line.find(temp_file)]
            newline = newline + objectpath+'\t\t'+modification_date
            diff_res = diff_res.replace(changed_line, newline)

    return "\n\n"+diff_res+"\n\n"
