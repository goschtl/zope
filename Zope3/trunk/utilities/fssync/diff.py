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

import os, commands, calendar, string

from common import getObjectDataTempfile

def getdiff(targetfile
            , objpath
            , dbpath
            , siteconfpath
            , diffoption=None):
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
        targetfile=os.path.join(os.path.abspath(os.curdir)
                                ,targetfile)
    if not os.path.exists(targetfile):
        return "sync [diff aborted] : Target file does not exist --- %s" \
               % (str(targetfile))
    if os.path.isdir(targetfile):
        return "sync [diff aborted] : Target file found to be a directory --- %s" \
               % (str(targetfile))
    if not os.path.exists(os.path.join(os.path.abspath(os.path.dirname(targetfile))
                                       ,'@@Zope')):
        return 'sync [diff aborted] : @@Zope administrative folder not found'

    if string.find(os.path.basename(targetfile), ' ')<>-1:
        targetfile = os.path.join(os.path.dirname(targetfile)
                                  , '\''+os.path.basename(targetfile)+'\'')

    if diffoption == '-1':
        from_file = os.path.join(os.path.dirname(targetfile)
                                 ,'@@Zope'
                                 ,'Original')
        to_file = targetfile
    elif diffoption == '-2':
        temp_file, objectpath, modification_date = getObjectDataTempfile(zodbtargetfile
                                                                         , objpath
                                                                         , dbpath
                                                                         , siteconfpath)
        from_file = targetfile
        to_file = temp_file
    elif diffoption == '-3':
        temp_file, objectpath, modification_date = getObjectDataTempfile(zodbtargetfile
                                                                         , objpath
                                                                         , dbpath
                                                                         , siteconfpath)
        from_file = os.path.join(os.path.dirname(targetfile)
                                 ,'@@Zope'
                                 ,'Original'
                                 ,os.path.basename(targetfile))
        to_file = temp_file

    diff_cmd ="""diff -a -b -B -c %s %s""" \
               % (from_file,to_file)
    diff_res = commands.getoutput(diff_cmd)
    diff_res = setOutput(diff_res
                         , temp_file
                         , objectpath
                         , modification_date)
    print diff_res

    if temp_file:
        os.remove(temp_file)

    return None

def getDiffDate(strdt):
    """Returns date in Day Mon DD hh:mm:ss YYYY format.
    """
    fmt_date=''
    if strdt:
        strdt = str(strdt)
        weekdays={0:'Mon'
                  ,1:'Tue'
                  ,2:'Wed'
                  ,3:'Thu'
                  ,4:'Fri'
                  ,5:'Sat'
                  ,6:'Sun'}
        months={1:'Jan'
                , 2:'Feb'
                , 3:'Mar'
                , 4:'Apr'
                , 5:'May'
                , 6:'Jun'
                , 7:'Jul'
                , 8:'Aug'
                , 9:'Sep'
                , 10:'Oct'
                , 11:'Nov'
                , 12:'Dec'}
        date=string.split(string.split(strdt,'T')[0],'-')
        time=string.split(string.split(strdt,'T')[1],'.')[0]
        day=weekdays[calendar.weekday(int(date[0])
                                      ,int(date[1])
                                      ,int(date[2]))]
        fmt_date=day+' '+months[int(date[1])]+' '+date[2]+' '+time+' '+date[0]

    return fmt_date

def setOutput(diff_res
              , temp_file
              , objectpath
              , modification_date):
    """Sets the diff output replacing it with original object
    path and modification datetime.
    """
    changed_line = ''
    modification_date = getDiffDate(modification_date)
    if temp_file:
        for line in string.split(diff_res,'\n'):
            if string.find(line,temp_file)<>-1:
                changed_line = line
                break
        if changed_line:
            newline = changed_line[:string.find(changed_line,temp_file)]
            newline = newline + objectpath+'\t\t'+modification_date
            diff_res = string.replace(diff_res, changed_line, newline)

    return "\n\n"+diff_res+"\n\n"
