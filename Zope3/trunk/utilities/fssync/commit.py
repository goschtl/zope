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

from zope.app.fssync.syncer import fromFS
from common import getZODBPath, createTempfile, getObject
from common import getApplicationRoot, traverseFS, checkConflictData
from common import isNewObject
from transaction import get_transaction

def commit(fspath, dbpath, siteconfpath, mode=None):
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
            original_path = mapping_paths[sandbox_path][0].strip()
            zopedb_path = mapping_paths[sandbox_path][1].strip()
            if isNewObject(sandbox_path):
                fsroot = sandbox_path[:sandbox_path.find(zopedb_path)]
                fsroot = os.path.abspath(fsroot)
                path = ''
                for object in zopedb_path.split('/')[1:]:
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
                if sandbox_path.find(vpath) < 0:
                    fmt_sandbox_path = commands.mkarg(sandbox_path)
                    fmt_original_path = commands.mkarg(original_path)

                    ob = getObject(zopedb_path, root)
                    zopedb_temp_file = createTempfile(ob, zopedb_path)
                    diff_cmd1 = ("diff -q -b %s %s; echo $?" %
                                 (fmt_original_path, zopedb_temp_file))
                    diff_res1 = commands.getoutput(diff_cmd1)
                    isConflict = int(diff_res1[-1])
                    diff_cmd2 = ("diff -q -b %s %s; echo $?" %
                                 (fmt_sandbox_path, fmt_original_path))
                    diff_res2 = commands.getoutput(diff_cmd2)
                    isCommitRequired = int(diff_res2[-1])

                    if checkConflictData(sandbox_path, zopedb_path):
                        isConflict = 1
                    if isConflict:
                        msg = ("%s Conflict, Uptodate checkin failed" %
                               zopedb_path)
                        print msg
                    else:
                        if not (isCommitRequired == isConflict == 0):
                            msg = ("%s  <--  %s" %
                                   (zopedb_path, zopedb_path.split('/')[-1]))
                            err = doCommit(sandbox_path, root)
                            if err is not None:
                                return err
                            print msg

                    if os.path.exists(zopedb_temp_file):
                        os.remove(zopedb_temp_file)

    return None


def doCommit(fspath, root, mode=None):
    container = ''
    objpath = getZODBPath(fspath)
    objname = objpath.split('/')[-1]
    path = objpath.split('/')[:-1]

    for item in path:
        if item:
            container = container +"['"+item+"']"
    try:
        if container:
            container=eval('root'+container)
        else:
            container=root
    except: # XXX which exception are we trying to catch?
        return 'sync [commit aborted] : invalid object path ---  %s' % objpath

    # Copying to ZODB
    fromFS(container, objname , os.path.dirname(fspath), mode)
    get_transaction().commit()

    if mode is None:
        # Copying to original
        f = open(fspath, 'r')
        data = f.read()
        f.close()
        original_path = os.path.join(os.path.dirname(fspath),
                                     '@@Zope', 'Original',
                                     os.path.basename(fspath))
        f = open(original_path, 'w')
        f.write(data.strip())
        f.close()
    return None
