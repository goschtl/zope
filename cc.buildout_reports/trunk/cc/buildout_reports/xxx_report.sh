#!/bin/bash
##############################################################################
#
# Copyright (c) 2002-2007 Zope Corporation and Contributors.
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

# ./xxx_report.sh [base] [output_file] [pattern]

PYTHON=`which python2.4`

PATTERN=$3
TMPFILE=`mktemp` 
TARGET=$2
FINDBASE=$1
SW_BASE=`dirname $0`

# find also finds hidden files
rm $TARGET
find $FINDBASE -wholename '*.svn' -prune -o -wholename '*.egg' -prune \
    -o -! -name '*~' -! -name '*.pyc' -print0 | \
    xargs -0 grep -niIs -A 3 -E "# $PATTERN" | \
    $PYTHON $SW_BASE/XXXreport2html.py /dev/stdin $TARGET >/dev/null
    
rm -f $TMPFILE
