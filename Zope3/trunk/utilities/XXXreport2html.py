##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Beautify a XXX report.

Creates a HTML file from a XXXReport file.

$Id: XXXreport2html.py,v 1.1 2002/12/07 16:52:08 ctheune Exp $
"""

import sys


if len(sys.argv) < 3:
    print "Usage: beautifyXXX.py <input-filename> <output-filename>"
    sys.exit()

inputname = sys.argv[1]
outputname = sys.argv[2]

inputfile = open(inputname, "r")
outputfile = open(outputname, "w")

# Scan the inputfile. All lines that are "---" are used as delimiters

comments = []
# This is file, line, context
current = ["", 0, []]
for x in inputfile.readlines():
    if x == "--\n":
        print ".",
        comments.append(current)
        current = ["", 0, []] 
        currentfile = None
        continue

    if not current[0]:
        splitted = x.split(":")
        current[0] = splitted[0]
        current[1] = splitted[1]
        x = ":".join(splitted[2:])
    else:
        splitted = x.split("-")
        x = "-".join(splitted[2:])
    current[2].append(x)

outputfile.write("""<html><head><title>XXX-Comment report for Zope 3</title>
</head>

<body>
<h1>Zope 3 - Developer report tools: XXX comments</h1>
<hr>
<h3>Summary</h3>
<p>
 There are currently %(commentcount)s XXX comments.
</p>
<hr/>
<h3>Listing</h3>
<ol>""" % {"commentcount" : len(comments)})

# Write the comments down

for x in comments:
    outputfile.write("""<li><b>File: %(filename)s:%(line)s</b><br/><pre>%(text)s</pre></li>""" % {'filename':x[0], 'line':x[1], 'text':"".join(x[2])})

outputfile.write("<ol></body></html>")
outputfile.flush()
outputfile.close()
