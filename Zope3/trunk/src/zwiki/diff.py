##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Browser View Components for WikiPages

$Id$
"""
from difflib import SequenceMatcher
from string import split, join

MAX_OLD_LINES_DISPLAY = 40
MAX_NEW_LINES_DISPLAY = 40


def textdiff(old_text, new_text, verbose=1):
    """
    generate a plain text diff, optimized for human readability,
    between two revisions of this page, numbering back from the latest.
    Alternately, a and/or b texts can be specified.
    """

    old = split(old_text, '\n')
    new = split(new_text, '\n')
    cruncher=SequenceMatcher(
        isjunk=lambda x: x in " \\t",
        a=old,
        b=new)

    r = []
    for tag, old_lo, old_hi, new_lo, new_hi in cruncher.get_opcodes():
        if tag == 'replace':
            if verbose: r.append('??changed:')
            r = r + _abbreviateDiffLines(old[old_lo:old_hi],'-',
                                         MAX_OLD_LINES_DISPLAY)
            r = r + _abbreviateDiffLines(new[new_lo:new_hi],'+',
                                         MAX_NEW_LINES_DISPLAY)
            r.append('')
        elif tag == 'delete':
            if verbose: r.append('--removed:')
            r = r + _abbreviateDiffLines(old[old_lo:old_hi],'-',
                                         MAX_OLD_LINES_DISPLAY)
            r.append('')
        elif tag == 'insert':
            if verbose: r.append('++added:')
            r = r + _abbreviateDiffLines(new[new_lo:new_hi],'',
                                         MAX_NEW_LINES_DISPLAY)
            r.append('')
        elif tag == 'equal':
            pass
        else:
            raise ValueError, 'unknown tag ' + `tag`

    return '\n' + join(r, '\n')


def _abbreviateDiffLines(lines, prefix, maxlines=5):
    output = []
    if maxlines and len(lines) > maxlines:
        extra = len(lines) - maxlines
        for i in xrange(maxlines - 1):
            output.append(prefix + lines[i])
        output.append(prefix + "[%d more line%s...]" %
                      (extra, ((extra == 1) and '') or 's')) # not working
    else:
        for line in lines:
            output.append(prefix + line)
    return output
