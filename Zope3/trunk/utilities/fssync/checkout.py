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

import string, os

from zope.app.fssync.syncer import toFS

from common import getObject, getApplicationRoot
from common import makeNewEntry, getObjectAdapter

def checkout(fspath
             , dbpath
             , siteconfpath
             , objpath):
    """Checks out objects from ZODB to the file system

    Downloads ZODB objects in file system to the specified path
    specified but -f option.
    """
    sandbox_path = fspath
    if not os.path.isabs(objpath):
        objpath = '/'+objpath
    objpath = os.path.abspath(objpath)
    root = getApplicationRoot(dbpath, siteconfpath)
    main_ob = getObject(objpath, root)
    ob_name = os.path.basename(objpath)
    if main_ob is not None:
        path = ''
        for dir in string.split(objpath[:string.rfind(objpath,ob_name)], '/')[1:-1]:
            path = os.path.join(path,dir)
            sandbox_path = os.path.join(fspath, path)
            admin_dir = os.path.join(os.path.dirname(sandbox_path), '@@Zope')
            entries_path = os.path.join(os.path.dirname(sandbox_path),
                                        '@@Zope'
                                        , 'Entries.xml')
            if not os.path.exists(sandbox_path):
                os.mkdir(sandbox_path)
            if not os.path.exists(admin_dir):
                os.mkdir(admin_dir)
            if not os.path.exists(entries_path):
                makeNewEntry(admin_dir)

            o_path = '/'+path
            ob = getObject(o_path, root)
            adapter = getObjectAdapter(ob)
            type = adapter.typeIdentifier()
            factory = adapter.factory()
            name = os.path.basename(o_path)
            makeNewEntry(admin_dir
                         , name
                         , type
                         , factory
                         , o_path)

        fspath = sandbox_path
        toFS(main_ob, ob_name, fspath)
        return None
    else:
        return "Invalid object path"
