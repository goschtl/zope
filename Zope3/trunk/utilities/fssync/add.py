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

from common import getZODBPath, getApplicationRoot, getObject
from common import getObjectAdapter, setPrint, IObjectDirectory
from zope.app.fssync.classes import FSAddRequest
from zope.component import getView, queryView
from zope.app.content.folder import Folder
from zope.app.fssync.syncer import toFS, fromFS
from zope.xmlpickle.xmlpickle import loads

from zope.component.view import viewService


env = os.environ

def add(fspath
        , dbpath
        , siteconfpath
        , newobjecttype
        , newobjectname):

    """Adds objects to File system

    Creates an object in the file system based on the object type
    passed with -t  option.
    """
    fspath = os.path.abspath(fspath)
    if not os.path.isdir(fspath):
        return 'sync [add aborted] : %s is not a directory' %(fspath)

    if not os.path.exists(os.path.join(fspath, '@@Zope')):
        return 'sync [add aborted] : @@Zope administrative folder not found in %s' \
               %(fspath)

    objpath = getZODBPath(fspath)
    root = getApplicationRoot(dbpath, siteconfpath)
    container = getObject(objpath, root)
    if container is None:
        container, name, path = getObject(objpath, root, 'Y')
        fsroot = os.path.abspath(fspath[:string.find(fspath, objpath)])
        location = os.path.abspath(os.path.join(fsroot, path[1:]))
        fromFS(container, name, location, 'T')

    container = getObject(objpath, root)

    adapter = getObjectAdapter(container)

    if newobjecttype:
        newobjecttype = '.'+newobjecttype
        for file in newobjectname:
            entries_path = os.path.join(os.path.join(fspath, os.path.dirname(file)),'@@Zope','Entries.xml')
            entries = {}
            if os.path.exists(entries_path):
                entries = loads(open(entries_path).read())
            if getObject(objpath+'/'+file, root) is not None:
                setPrint('Object already exist in the ZODB : %s' \
                          %(os.path.join(fspath,file)))
            elif entries.has_key(os.path.basename(file)):
                setPrint('Object already exist in sandbox : %s' \
                          %(os.path.join(fspath,file)))
            else:
                err = addObject(adapter, fspath, newobjecttype, file, objpath)
                if err is not None:
                    setPrint(err)
                    break
    else:
        for file in newobjectname:
            entries_path = os.path.join(os.path.join(fspath, os.path.dirname(file)),'@@Zope','Entries.xml')
            entries = {}
            if os.path.exists(entries_path):
                entries = loads(open(entries_path).read())
            if getObject(objpath+'/'+file, root) is not None:
                setPrint('Object already exist in the ZODB : %s' \
                          %(os.path.join(fspath,file)))
            elif entries.has_key(os.path.basename(file)):
                setPrint('Object already exist in sandbox : %s' \
                          %(os.path.join(fspath,file)))
            else:
                newobjecttype = '.'+string.split(file,'.')[-1]
                err = addObject(adapter
                                , fspath
                                , newobjecttype
                                , file
                                , objpath)
                if err is not None:
                    setPrint(err)
    return None

def addObject(adapter
              , fspath
              , newobjecttype
              , newobjectname
              , objpath):

    mode = 'N'
    if IObjectDirectory.isImplementedBy(adapter):
        request = FSAddRequest()
        view = queryView(adapter, newobjecttype, request)
        if view is not None:
            newobjectpath = os.path.abspath(os.path.join(fspath, newobjectname))
            if not os.path.exists(os.path.dirname(newobjectpath)):
                return 'Nothing known about : %s'%(newobjectpath)
            newobject = view.create()
            objpath = objpath+'/'+newobjectname
            objectname = os.path.basename(newobjectpath)
            newobjectpath = os.path.dirname(newobjectpath)
            dir_list = createAdminFolder(newobjectpath, objpath)
            keys = dir_list.keys()
            keys.sort()
            for sl_no in keys:
                ob = Folder()
                toFS(ob, dir_list[sl_no][2], dir_list[sl_no][0], mode, dir_list[sl_no][1])
            toFS(newobject, objectname, newobjectpath, mode, objpath)
        else:
            newobjectpath = os.path.abspath(os.path.join(fspath, newobjectname))
            if not os.path.exists(newobjectpath):
                return 'Nothing known about : %s'%(newobjectpath)
            view = getView(adapter, '.', request)
            newobject = view.create(newobjectpath)
            objpath = os.path.abspath(objpath+'/'+newobjectname)
            objectname = os.path.basename(newobjectpath)
            newobjectpath = os.path.dirname(newobjectpath)
            path_list = string.split(newobjectname, os.sep)
            if len(path_list) > 1:
                if path_list[-1] != objectname:
                    return 'Nothing known about : %s'%(path_list[-1])

                dir_list = createAdminFolder(newobjectpath, objpath)
                keys = dir_list.keys()
                keys.sort()
                for sl_no in keys:
                    ob = Folder()
                    toFS(ob, dir_list[sl_no][2], dir_list[sl_no][0], mode, dir_list[sl_no][1])
            toFS(newobject, objectname, newobjectpath, mode, objpath)

    else:
        return 'Not a container type : %s' %(os.path.basename(fspath))
    return None

def createAdminFolder(fspath, objpath, name=None, data={}):
    if name is not None:
        data[len(string.split(objpath, '/'))] = (fspath, objpath, name)
    if not os.path.exists(os.path.join(fspath, '@@Zope')):
        return createAdminFolder(os.path.dirname(fspath), os.path.dirname(objpath), os.path.basename(fspath))
    return data

def addTypes(dbpath
             , siteconfpath):
    root = getApplicationRoot(dbpath, siteconfpath)
    f = Folder()
    adapter = getObjectAdapter(f)
    request = FSAddRequest()
    allviews = viewService.all()['default']
    setPrint("\nALL AVAILABLE TYPES")
    setPrint("====================================================\n")
    for view in allviews:
        try:
            if len(view)>1 and view[0] == '.':
                doc = getView(adapter, view, request).__doc__
                setPrint(' %s  \n %s \n\n' % (view, doc))
        except:
            pass
