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

import os, commands

from common import getZODBPath, createTempfile, getObject
from common import mapFS, traverseFS, checkConflictData, getApplicationRoot
from common import isNewObject, getFSRoot

from zope.app.fssync.syncer import toFS

def update(fspath, dbpath, siteconfpath):
    """Updates the checked out objects in the file system from a ZODB

    updates the files in the sandbox based on the file system path given
    by -f option.
    """
    root = getApplicationRoot(dbpath, siteconfpath)
    if os.path.isdir(fspath):
        fsparent = os.path.dirname(os.path.abspath(fspath))
        if not os.path.exists(os.path.join(fsparent, '@@Zope')):
            module_list = os.listdir(os.path.abspath(fspath))
            if '@@Zope' in module_list:
                module_list.remove('@@Zope')
                for module in module_list:
                    fsp = os.path.join(fspath, module)
                    updateSettings(fsp, root)
            else:
                return ('sync [update aborted] : '
                        '@@Zope administrative folder not found in %s' %
                        fspath)
        else:
            updateSettings(fspath, root)
    else:
        updateSettings(fspath, root)

def updateSettings(fspath, root):
    """does the settings for update
    """
    fspath = os.path.abspath(fspath)
    if os.path.isdir(fspath):
        admin_dir = os.path.join(fspath,'@@Zope')
    else:
        admin_dir = os.path.join(os.path.dirname(fspath),'@@Zope')
    if not os.path.exists(admin_dir):
        return ('sync [update aborted] : '
                '@@Zope administrative folder not found in %s' %
                fspath)

    mappings = {}
    mapping_paths = {}
    mapping_paths.update(traverseFS(fspath, mapping_paths))

    for sandbox_path in mapping_paths.keys():
        original_path = mapping_paths[sandbox_path][0].strip()
        zopedb_path = mapping_paths[sandbox_path][1].strip()
        if checkConflictData(sandbox_path, zopedb_path):
            print 'C', zopedb_path[1:]
        else:
            if not isNewObject(sandbox_path):
                mappings[zopedb_path] = sandbox_path

                fmt_sandbox_path = commands.mkarg(sandbox_path)
                fmt_original_path = commands.mkarg(original_path)

                ob = getObject(zopedb_path, root)
                zopedb_temp_file = createTempfile(ob, zopedb_path)
                diff3_cmd = "diff3 -a %s %s %s" % (fmt_sandbox_path,
                                                   fmt_original_path,
                                                   zopedb_temp_file)
                diff3_res = commands.getoutput(diff3_cmd)
                if len(diff3_res.strip()) > 1:
                    diffverify = diff3_res[0:5].strip()
                    if diffverify == '====1':
                        print 'M', zopedb_path[1:]
                    elif diffverify == '====2':
                        doUpdate('C', ob, zopedb_path, sandbox_path)
                        print 'M', zopedb_path[1:]
                    elif diffverify == '====3':
                        doUpdate('U', ob, zopedb_path, sandbox_path)
                    elif diffverify == '====':
                        diff3_cmd = ("diff3 -a -m %s %s %s; echo $?" %
                                     (fmt_sandbox_path, fmt_original_path,
                                      zopedb_temp_file))
                        diff3_res = commands.getoutput(diff3_cmd)
                        diff3_res = diff3_res.replace(zopedb_temp_file,
                                                      zopedb_path)
                        if diff3_res[-1] == '0':
                            print 'Merging changes in', zopedb_path[1:]
                        else:
                            print 'C Merging changes in', zopedb_path[1:]

                        f = open(sandbox_path, 'w')
                        f.write(diff3_res[:-1].strip())
                        f.close()
                        doUpdate('C', ob, zopedb_path, sandbox_path)

                if os.path.exists(zopedb_temp_file):
                    os.remove(zopedb_temp_file)

    if os.path.isdir(fspath):
        objectroot = getZODBPath(fspath)
        fsroot = getFSRoot(fspath)
        mapFS(mappings, root, objectroot, fsroot)

def doUpdate(mode, ob, zopedb_path, sandbox_path):
    """Updates data
    """
    sandbox_path = os.path.dirname(sandbox_path)
    ob_name = zopedb_path.split('/')[-1]
    if mode == 'U':
        if ob is not None:
            toFS(ob, ob_name, sandbox_path)
    elif mode == 'C':
        if ob is not None:
            toFS(ob, ob_name, sandbox_path, mode)
