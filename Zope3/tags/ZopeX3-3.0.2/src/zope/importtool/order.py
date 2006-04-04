#! /usr/bin/env python2.3
##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""
This tool basically can be used to rearrange and order imported
python packages in a particular format for .py files.

Import Order:-
   1. import modules from standard python library/global packages
   2. import modules from the zope package
   3. import modules from the zope.app package

.py [-dfhst] [file/directory]

-d / --dir
    It will sort all the .py files imported python packages in the
    entire directory .

-D / --display
   Displays Import order for all .py files in the specified path.

-f / --file
   It will order all imported python packages in a file.

-s / --split
   It splits up multiple import modules in a single import statement
   into multiple import statements.


-t / --test
   It Displays Import order for all py files in the specified path and
   doesn't write importorder into .py file.

$Id$
"""

import getopt
import glob
import os
import string
import sys
import tokenize


PYTHONFILE_FILTER = '*.py'
FROMIMPORT = 'from '
IMPORT = 'import '
FROMIMPORT_ZOPE = 'from zope'
IMPORT_ZOPE = 'import zope'
FROMIMPORT_ZOPE_APP = 'from zope.app'
IMPORT_ZOPE_APP = 'import zope.app'
NO_CHARACTERS = 80


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


def importOrderProcessing(path, display=None, write=None, split=None):
    """process import order for all .py files in the specified path."""
    pyfiles = getPythonFiles(path)

    print '*****************************************************************'
    for file in pyfiles:
        print '** File : %s   **\n' % (file)
        import_block = getFileImportOrder(file, split)
        import_order = import_block['import_order']
        non_import_order = import_block['non_import_order']
        if display:
            print non_import_order
            print '**.......................................................**'
            print import_order
        if write:
            writeFormatedContent(file, import_order, non_import_order)


    print '*****************************************************************'


def getFileImportOrder(file, split=None):
    """returns formatted imported packages content"""
    import_content = getFileImportContent(file)
    import_list = appendImportsToList(import_content)

    #separating from and import statements
    imp_list = filterList(import_list, 'import ')
    from_list = filterList(import_list, 'from ')

    #extracting non import content
    non_import_block = removeList(import_list, imp_list)
    non_import_block = removeList(non_import_block, from_list)
    non_import_block_fmt = formateBlock(non_import_block)

    #comma separated imports into individual import statements
    if split:
        imp_list = individualImportLines(imp_list)
        from_list = individualImportLines(from_list)

    #extracting zope.app package imports
    zope_app_imp_list = filterList(imp_list, IMPORT_ZOPE_APP)
    zope_app_from_list = filterList(from_list, FROMIMPORT_ZOPE_APP)

    rem_imp_list1 = removeList(imp_list, zope_app_imp_list)
    rem_from_list1 = removeList(from_list, zope_app_from_list)

    #extracting zope package imports
    zope_imp_list = filterList(rem_imp_list1, IMPORT_ZOPE)
    zope_from_list = filterList(rem_from_list1, FROMIMPORT_ZOPE)

    #extracting global package imports
    global_imp_list = removeList(rem_imp_list1, zope_imp_list)
    global_from_list = removeList(rem_from_list1, zope_from_list)

    #formating the global, zope and zope.app package imports
    format_import_content = mergeAllBlocks(global_imp_list,
                                           zope_imp_list,
                                           zope_app_imp_list,
                                           global_from_list,
                                           zope_from_list,
                                           zope_app_from_list)

    #merging import block and non import block
    non_import_block_fmt = string.strip(non_import_block_fmt)
    if len(non_import_block_fmt) > 0:
        non_import_block_fmt += '\n\n'

    fmt_content = format_import_content + non_import_block_fmt

    return {'import_order':fmt_content,
            'non_import_order':import_content}


def getFileImportContent(file):
    """returns the imports content available at the top in the .py file"""
    import_list = []
    lines = []
    import_block_start_indx = 0
    import_block_end_indx = 0
    index = 0
    for t in tokenize.generate_tokens(open(file, 'rU').readline):
        type, string, start, end, line = t
        line_no = start[0]
        line_len = len(line)

        if line_no not in lines:
            lines.append(line_no)
            index += line_len
        if string in ['from','import'] and line not in import_list:
            if len(import_list) == 0:
                import_block_start_indx = (index - line_len)
            import_list.append(line)
            import_block_end_indx = index
        elif string in ['def', 'class']:
            break

    fc = open(file, 'r').read()
    return fc[import_block_start_indx-4:import_block_end_indx-4]


def appendImportsToList(import_content):
    """returns list of imports of the file"""
    import_list = import_content.split('\\')
    if len(import_list) > 1:
        import_list = concatinateBreakImports(import_list)
    else:
        import_list = import_content.split('\n')

    return import_list


def concatinateBreakImports(import_list):
    """concatinate imports into single item in a list"""
    indx = 1
    concate_list = []
    for item in import_list:
        if indx == 1:
            concate_list += item.split('\n')
        else:
            concate_item = []
            item = string.lstrip(item)
            item_list = item.split('\n')
            concate_litem = concate_list[-1:][0]
            item_list_fitem = item_list[:1][0]
            concate_item.append(concate_litem + item_list_fitem)
            concate_list = concate_list[:-1] + concate_item + item_list[1:]
        indx += 1

    return concate_list


def filterList(list, filter):
    """returns filtered list"""
    filter_list = [item for item in list
                if item.startswith(filter)]
    filter_list.sort()
    return filter_list

def individualImportLines(import_list):
    """changes comma separated imports to individual import lines"""
    import_str = 'import '
    new_import_list = []
    for item in import_list:
        if item.find(',') > -1 and (item.startswith('from ') or
                                    item.startswith('import ')):
            import_item_split = item.split('import ')
            from_import_item = import_item_split[0]
            comma_imports = import_item_split[1].split(',')
            new_list = []
            for mod_item in comma_imports:
                mod_item = string.lstrip(mod_item)
                new_list.append(from_import_item + import_str + mod_item)
            new_import_list += new_list
        else:
            new_import_list.append(item)

    return new_import_list


def removeList(list, rem_list):
    return [item for item in list
            if item not in rem_list]

def mergeAllBlocks(global_imp_list, zope_imp_list, zope_app_imp_list,
                   global_from_list, zope_from_list, zope_app_from_list):
    """merges global, zope and zope.app imports """
    import_block = ''
    global_imp_block = formateBlock(global_imp_list)
    global_from_block = formateBlock(global_from_list)
    zope_imp_block = formateBlock(zope_imp_list)
    zope_from_block = formateBlock(zope_from_list)
    zope_app_imp_block = formateBlock(zope_app_imp_list)
    zope_app_from_block = formateBlock(zope_app_from_list)

    import_block += formatsFromAndImportBlock(global_imp_block,
                                              global_from_block)

    import_block += formatsFromAndImportBlock(zope_imp_block,
                                              zope_from_block)

    import_block += formatsFromAndImportBlock(zope_app_imp_block,
                                              zope_app_from_block)

    return import_block


def formatsFromAndImportBlock(imp_block, from_block):
    """formats from and import block"""
    import_block = ''
    if imp_block is not '' or from_block is not '':
        import_block += imp_block
        import_block += from_block
        import_block += '\n'
    return import_block


def formateBlock(imp_list):
    """formats import blocks"""
    import_block = ''
    if imp_list is not None:
        for item in imp_list:
            if len(item) > NO_CHARACTERS:
                import_block += formatingLargerImports(item)
            else:
                import_block += str(item) + '\n'
    return import_block

def formatingLargerImports(import_content):
    """formates if imports greater than 80 character"""
    formatted_line = ''
    import_fline = import_content[:NO_CHARACTERS]

    dot_indx = import_fline.rfind('.')
    blank_space_indx = import_fline.rfind(' ')

    split_line_indx = 0
    if dot_indx > -1:
        split_line_indx = dot_indx
        if blank_space_indx > -1 and blank_space_indx < dot_indx:
            split_line_indx = blank_space_indx
    elif blank_space_indx > -1:
        split_line_indx = blank_space_indx
        if dot_indx > -1 and dot_indx < blank_space_indx:
            split_line_indx = blank_space_indx

    split_line_indx += 1

    formatted_line += import_content[:split_line_indx] +'\\\n'
    if import_content.startswith(IMPORT):
        formatted_line += ('       ' +
                           import_content[split_line_indx:] + '\n')
    elif import_content.startswith(FROMIMPORT):
        formatted_line += ('     ' +
                           import_content[split_line_indx:] + '\n')

    return formatted_line


def writeFormatedContent(file, fmt_content, non_fmt_content):
    """writes formatted content into the file"""

    fp = open(file, 'r')
    file_content = fp.read()
    fp.close()

    fp = open(file, 'w')
    rep_content = string.replace(file_content, non_fmt_content,
                                 fmt_content)
    fp.write(rep_content)
    fp.close()


def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        opts, args = getopt.getopt(sys.argv[1:], "dDfhst",
                                   ["help", "dir", "file", "display",
                                    "split", "test"])
    except getopt.error, msg:
        print msg
        print "Try `python %s -h' for more information." % argv[0]
        return 2

    path = None
    display = None
    write = True
    split = None

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
        elif k in ("-s", "--split"):
            path = args[0]
            split = True
        elif k in ("-t", "--test"):
            path = args[0]
            display = True
            write = False

    importOrderProcessing(path, display, write, split)
    return 0
