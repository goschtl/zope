#! /usr/bin/env python2.3
##############################################################################
#
# Copyright (c) 2001 - 2004 Zope Corporation and Contributors 
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
This tool basically can be used to 

.py [-dfhst] [file/directory]

-d / --dir
    It will fix Copyright for all .py files in the
    entire directory .

-D / --display
   Displays  Copyright for all .py files in the specified path. 

-f / --file
   It will fix copyright in a file.

-t / --test
   It Displays copyright for all py files in the specified path and
   doesn't write copyright into .py file. 

"""

import getopt
import glob
import os
import string
import sys
import commands
import re

PYTHONFILE_FILTER = '*.py'
rec = re.compile(r'(\d{4})')

def getPythonFiles(path):
    """returns list of .py files in the specified path"""
    pyfiles = []
    if not os.path.exists(path):
        print >> sys.stderr, '** Error: '+ path +' not a valid path **'
        sys.exit(0)

    #checking path is file
    if os.path.isfile(path):
        pyfiles.append(path)

    #checking path is a directory
    elif os.path.isdir(path):
        path = os.path.join(path, PYTHONFILE_FILTER)
        path, filter = os.path.split(path)
        pyfiles.extend(glob.glob(os.path.join(path, filter)))

        #checking in sub directories
        for root, dirs, files in os.walk(path):
            for dir in dirs:
                pyfiles.extend(glob.glob(\
                    os.path.join(root, dir, filter)))
    return pyfiles


def headerProcessing(path, display=None, write=None):
    """process the header for all .py files in the specified path."""
    pyfiles = getPythonFiles(path)

    print '*****************************************************************'
    for file in pyfiles:
        print '** File : %s   **' % (file)
        header_block = getFileHeader(file)
        formatted_header_content = header_block['formatted_header']
        non_formatted_header_content = header_block['non_formatted_header']
        if display:
	    print non_formatted_header_content,
            print '**.....................................................**'
            print formatted_header_content
        if write:
            writeFormatedContent(file,
                                 formatted_header_content,
                                 non_formatted_header_content)
    print '****************************************************************'
        

def getFileHeader(file):
    """returns header content"""
    header_content = getFileHeaderContent(file, 'line')
    format_header_content = fixheaderSection(file)
    return {'formatted_header':format_header_content,
            'non_formatted_header':header_content}

def getFileHeaderContent(file, check):
    """returns the line with copyright information 
    available at the top in the .py file"""
    fc = open(file, 'r')
    data_list = fc.readlines()
    req_lines = data_list[0:5]
    for line in req_lines:
        if string.find(line, 'Copyright') > -1 : 
	    if check == 'line':
		return line
	    else:
                return rec.findall(line)[0]
    return 'Copyright information not found'
    
def fixheaderSection(file):
    """returns the header content after checking the modified year in the .py file"""	
    try:
	cmd = commands.getoutput('svn info %s | grep Last\ Changed\ Date'%(file,))
	myear = rec.findall(cmd)[0]
    except:	
	return 'Last changed year not found'
    creation_year = getFileHeaderContent(file, 'year')
    if myear == creation_year:
        formatted_content = '# Copyright (c) ' + creation_year + \
	                    ' Zope Corporation and Contributors. \n'
    else:
        formatted_content = '# Copyright (c) ' + creation_year +' - ' + myear + \
                            ' Zope Corporation and Contributors. \n'	    
    return formatted_content

def writeFormatedContent(file, fmt_content, non_fmt_content):
    """writes formatted content into the file"""
    fp = open(file, 'r')
    file_content = fp.read()
    fp.close()
    
    fp = open(file, 'w')
    rep_content = string.replace(file_content, non_fmt_content, fmt_content)
    fp.write(rep_content)
    fp.close()


if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:], "dDfht",
		["help", "dir", "file", "display", "test"])
    except getopt.error, msg:
        print msg
        print "Try `python %s -h' for more information." % argv[0]
        sys.exit(2)
        
    path = args[0]
    display = None
    write = True
    split = None
    opts.sort()

    for k, v in opts:
        if k in ("-h", "--help"):
            print __doc__
            sys.exit(0)
        elif k in ("-d", "--dir"):
            path = args[0]
        elif k in ("-f", "--file"):
            path = args[0]
        elif k in ("-D", "--display"):
            path = args[0]
            display = True
        elif k in ("-t", "--test"):
            path = args[0]
            display = True
            write = False

    headerProcessing(path, display, write)
