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
"""

$Id: OSEmulators.py,v 1.2 2002/06/10 23:29:35 jim Exp $
"""

import stat
import time

months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

mode_table = {
        '0':'---',
        '1':'--x',
        '2':'-w-',
        '3':'-wx',
        '4':'r--',
        '5':'r-x',
        '6':'rw-',
        '7':'rwx'
        }


def ls_longify((filename, stat_info)):
    """Formats a directory entry similarly to the 'ls' command.
    """
    
    # Note that we expect a little deviance from the result of os.stat():
    # we expect the ST_UID and ST_GID fields to contain user IDs.
    username = str(stat_info[stat.ST_UID])[:8]
    grpname = str(stat_info[stat.ST_GID])[:8]

    mode_octal = ('%o' % stat_info[stat.ST_MODE])[-3:]
    mode = ''.join(map(mode_table.get, mode_octal))
    if stat.S_ISDIR (stat_info[stat.ST_MODE]):
        dirchar = 'd'
    else:
        dirchar = '-'
    date = ls_date (long(time.time()), stat_info[stat.ST_MTIME])
    return '%s%s %3d %-8s %-8s %8d %s %s' % (
            dirchar,
            mode,
            stat_info[stat.ST_NLINK],
            username,
            grpname,
            stat_info[stat.ST_SIZE],
            date,
            filename
            )


def ls_date (now, t):
    """Emulate the 'ls' command's date field.  It has two formats.
       If the date is more than 180 days in the past or future, then
       it's like this:
         Oct 19  1995
       otherwise, it looks like this:
         Oct 19 17:33
    """
    try:
        info = time.localtime(t)
    except:
        info = time.localtime(0)

    # 15,600,000 == 86,400 * 180
    if abs((now - t) > 15600000):
        return '%s %2d %5d' % (
                months[info[1]-1],
                info[2],
                info[0]
                )
    else:
        return '%s %2d %02d:%02d' % (
                months[info[1]-1],
                info[2],
                info[3],
                info[4]
                )


def msdos_longify((file, stat_info)):
    """This matches the output of NT's ftp server (when in MSDOS mode)
       exactly.
    """
    if stat.S_ISDIR(stat_info[stat.ST_MODE]):
        dir = '<DIR>'
    else:
        dir = '     '
    date = msdos_date(stat_info[stat.ST_MTIME])
    return '%s       %s %8d %s' % (date, dir, stat_info[stat.ST_SIZE], file)


def msdos_date(t):
    try:
        info = time.gmtime(t)
    except:
        info = time.gmtime(0)

    # year, month, day, hour, minute, second, ...
    if info[3] > 11:
        merid = 'PM'
        info[3] = info[3] - 12
    else:
        merid = 'AM'

    return '%02d-%02d-%02d  %02d:%02d%s' % (
            info[1], info[2], info[0]%100, info[3], info[4], merid )
