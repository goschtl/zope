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

import os, string, commands

from zope.app.fssync.syncer import fromFS
from common import getZODBPath, createTempfile, getObject
from common import getApplicationRoot, traverseFS, checkConflictData
from common import isNewObject, setPrint
from transaction import get_transaction

env = os.environ

def commit(fspath
           , dbpath
           , siteconfpath
           , mode=None):
    """Checks in from file system to ZODB

    Saves the unconflict files in ZODB as Zope objects from the
    file system.
    """
    fspath = os.path.abspath(fspath)
    vpath = '<>'
    if os.path.isdir(fspath):
        admin_dir = os.path.join(fspath,'@@Zope')
    else:
        admin_dir = os.path.join(os.path.dirname(fspath),'@@Zope')
    if not os.path.exists(admin_dir):
        return 'sync [commit aborted] : @@Zope administrative folder not found'

    root = getApplicationRoot(dbpath, siteconfpath)
    if mode == 'F':
        err = doCommit(fspath, root, mode)
        if err is not None:
            return err
    else:
        mapping_paths = traverseFS(fspath, {})
        for sandbox_path in mapping_paths.keys():
            original_path = string.strip(mapping_paths[sandbox_path][0])
            zopedb_path = string.strip(mapping_paths[sandbox_path][1])
            if isNewObject(sandbox_path):
                fsroot = os.path.abspath(sandbox_path[:string.find(sandbox_path
                                                                   , zopedb_path)])
                path = ''
                for object in string.split(zopedb_path,'/')[1:]:
                    path = os.path.join(path,object)
                    newobjpath = os.path.join(fsroot,path)
                    if isNewObject(newobjpath):
                        err = doCommit(newobjpath, root, 'F')
                        if err is not None:
                            return err
                        if os.path.isdir(newobjpath):
                            vpath = newobjpath
                            break
            else:
                if string.find(sandbox_path,vpath)==-1:
                    fmt_sandbox_path = ''
                    fmt_original_path = ''
                    for dir in string.split(sandbox_path,os.sep):
                        if string.find(dir, ' ')<>-1:
                            fmt_sandbox_path = os.path.join(fmt_sandbox_path
                                                            , '\''+dir+'\'')
                        else:
                            fmt_sandbox_path = os.path.join(fmt_sandbox_path
                                                            , dir)

                    for dir in string.split(original_path,os.sep):
                        if string.find(dir, ' ')<>-1:
                            fmt_original_path = os.path.join(fmt_original_path
                                                             , '\''+dir+'\'')
                        else:
                            fmt_original_path = os.path.join(fmt_original_path
                                                             , dir)
                    fmt_sandbox_path = os.sep + fmt_sandbox_path
                    fmt_original_path = os.sep + fmt_original_path

                    ob = getObject(zopedb_path, root)
                    zopedb_temp_file = createTempfile(ob, zopedb_path)
                    diff_cmd1 = """diff -q -b %s %s;echo $?""" \
                                %(fmt_original_path, zopedb_temp_file)
                    diff_res1 = commands.getoutput(diff_cmd1)
                    isConflict = int(diff_res1[-1])
                    diff_cmd2 = """diff -q -b %s %s;echo $?""" \
                                %(fmt_sandbox_path, fmt_original_path)
                    diff_res2 = commands.getoutput(diff_cmd2)
                    isCommitRequired = int(diff_res2[-1])

                    if checkConflictData(sandbox_path, zopedb_path):
                        isConflict = 1
                    if isConflict:
                        msg = "%s Conflict, Uptodate checkin failed" \
                              %(zopedb_path)
                        setPrint(msg)
                    else:
                        if not (isCommitRequired == isConflict == 0):
                            msg = "%s  <--  %s" \
                                  %(zopedb_path, string.split(zopedb_path,'/')[-1])
                            err = doCommit(sandbox_path, root)
                            if err is not None:
                                return err
                            setPrint(msg)

                    if os.path.exists(zopedb_temp_file):
                        os.remove(zopedb_temp_file)

    return None


def doCommit(fspath, root, mode=None):
    container = ''
    objpath = getZODBPath(fspath)
    objname = string.split(objpath, '/')[-1]
    path = string.split(objpath, '/')[:-1]

    for item in path:
        if item:
            container = container +'[\''+item+'\']'
    try:
        if container:
            container=eval('root'+container)
        else:
            container=root
    except:
        return 'sync [commit aborted] : invalid object path ---  %s' \
               %(objpath)

    #copying to ZODB
    fromFS(container, objname , os.path.dirname(fspath), mode)
    get_transaction().commit()

    if mode is None:
        #copying to original
        f = open(fspath, 'r')
        data = f.read()
        f.close()
        original_path = os.path.join(os.path.dirname(fspath)
                                     ,'@@Zope'
                                     ,'Original'
                                     ,os.path.basename(fspath))
        f = open(original_path, 'w')
        f.write(string.strip(data))
        f.close()
    return None
