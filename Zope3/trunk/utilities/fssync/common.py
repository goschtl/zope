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

import os, tempfile

from zope.app.fssync.fsregistry import getSynchronizer
from zope.app.fssync.syncer import toFS
from zope.app import Application
from zope.app.interfaces.dublincore import IZopeDublinCore
from zope.app.interfaces.fssync import IObjectEntry
from zope.app.interfaces.fssync import IObjectFile, IObjectDirectory
from zope.app.traversing import traverse, getPath
from zope.component import queryAdapter, getService
from zope.exceptions import NotFoundError
from zope.xmlpickle import dumps, loads

def getObjectAdapter(ob):
    """Returns the object adapter.
    """
    syncService = getService(ob, 'FSRegistryService')
    return syncService.getSynchronizer(ob)

def getApplicationRoot(dbpath, siteconfpath):
    """Returns the application root.
    """
    app = Application(dbpath, siteconfpath)
    return app()

def getObject(objpath, root, prev=None, name=None):
    """Gets the object from ZODB.
    """
    if prev is None:
        try:
            return traverse(root,objpath)
        except: # XXX which exception are we trying to catch?
            return None
    else:
        try:
            ob = traverse(root,objpath)
            return ob, name, objpath
        except: # XXX which exception are we trying to catch?
            # XXX Why return (X, Y, Z)[0] and not just X?
            return (getObject(os.path.dirname(objpath), root, 'Y',
                              os.path.basename(objpath)), name, objpath)[0]

def getNewObject(ob, folders, files):
    """Returns the entire tree of a ZODB object.
    """
    adapter = getObjectAdapter(ob)
    path = ''
    try:
        path = str(getPath(ob))
    except TypeError:
        # XXX Really?
        pass

    if IObjectFile.isImplementedBy(adapter):
        files.append(path)
    else:
        folders.append(path)
        for cname, cob in  adapter.contents():
            getNewObject(cob, folders, files)
    return folders, files

def getZODBPath(targetfile, key=None):
    """Returns the physical path of an object in the ZODB
    of a filesysten representation.
    """
    targetfile = os.path.abspath(targetfile)
    entries_path = os.path.join(os.path.dirname(targetfile),
                                '@@Zope', 'Entries.xml')
    entries = loads(open(entries_path).read())
    if key is None:
        objectpath = entries[os.path.basename(targetfile)]['path']
    else:
        try:
            objectpath = entries[os.path.basename(targetfile)][key]
        except: # XXX which exception are we trying to catch?
            return None
    return objectpath

def isNewObject(targetfile):
    """Determines if the object in the filesystem is new.
    """
    targetfile = os.path.abspath(targetfile)
    entries_path = os.path.join(os.path.dirname(targetfile),
                                '@@Zope', 'Entries.xml')
    entries = loads(open(entries_path).read())
    return entries[os.path.basename(targetfile)].has_key('isNew')

def getObjectData(ob):
    """Returns the data of a ZODB object.
    """
    adapter = getObjectAdapter(ob)
    return adapter.getBody()

def getObjectDataTempfile(targetfile, objpath, dbpath, siteconfpath):
    """Returns the data of a particular object in ZODB.
    """
    root = getApplicationRoot(dbpath, siteconfpath)
    objectpath = getZODBPath(targetfile)
    ob = getObject(objectpath, root)
    adapter = adapter = getObjectAdapter(ob)
    dublincore_adapter = queryAdapter(ob, IZopeDublinCore)
    modification_date = dublincore_adapter.ModificationDate()
    object_data = adapter.getBody()
    temp_file = tempfile.mktemp('tmp')
    fo = open(temp_file,'w')
    fo.write(object_data.strip())
    fo.close()
    return temp_file, objectpath, modification_date


def createTempfile(ob, objectpath):
    """Creates a temporaty file in the filesystem and write ob's data to it.
    XXX argument 'objectpath' is unused.
    """
    objectdata = getObjectData(ob)
    temp_file = tempfile.mktemp('tmp')
    fo = open(temp_file,'w')
    fo.write(objectdata.strip())
    fo.close()
    return temp_file

def mapFS(mappings, root, objectroot, fsroot):
    """Returns the new object list in the zopedb which
    are not available in the filesystem.
    """
    ob = getObject(objectroot, root)
    folders, files = getNewObject(ob, [], [])
    for folder in folders:
        path = fsroot
        for part in folder.split('/'):
            path = os.path.join(path, part)
        if not os.path.exists(path):
            location = os.path.dirname(path)
            ob = getObject(folder, root)
            ob_name = folder.split('/')[-1]
            toFS(ob, ob_name, location)
    for file in files:
        path = fsroot
        for part in file.split('/'):
            path = os.path.join(path, part)
        if not os.path.exists(path):
            location = os.path.dirname(path)
            ob = getObject(file, root)
            ob_name = file.split('/')[-1]
            toFS(ob, ob_name, location)

def traverseFS(fspath, mapping_paths):
    """Traverse through the filesystem.
    """
    if os.path.isdir(fspath):
        root = fspath
        dirlist = os.listdir(root)
        for item in dirlist:
            if item != '@@Zope':
                fspath = os.path.join(root,item)
                if os.path.isdir(fspath):
                    traverseFS(fspath, mapping_paths)
                else:
                    sandbox_path = fspath
                    original_path = os.path.join(os.path.dirname(fspath),
                                                 '@@Zope', 'Original',
                                                 os.path.basename(fspath))
                    if os.path.exists(original_path):
                        zopedb_path = getZODBPath(fspath)
                        mapping_paths[sandbox_path] = [original_path,
                                                       zopedb_path]
    else:
        sandbox_path = fspath
        original_path = os.path.join(os.path.dirname(fspath),
                                     '@@Zope', 'Original',
                                     os.path.basename(fspath))
        if os.path.exists(original_path):
            zopedb_path = getZODBPath(fspath)
            mapping_paths[sandbox_path] = [original_path, zopedb_path]

    return mapping_paths

def checkConflictData(sandbox_path, zopedb_path):
    """Checks for conflict data in the filesystem.
    """
    f = open(sandbox_path,'r')
    data = f.read()
    f.close()
    filter1 = '<<<<<<< %s' % (sandbox_path)
    filter2 = '>>>>>>> %s' % (zopedb_path)
    return data.find(filter1) >= 0 and data.find(filter2) >= 0

def makeNewEntry(admin_dir, name=None, type=None, factory=None,
                 objpath=None, isNew=None):
    """Edits the Entries.xml file.
    """
    entries = {}
    entries_path = os.path.join(admin_dir, 'Entries.xml')
    if os.path.exists(entries_path):
        entries = loads(open(entries_path).read())
    if not entries.has_key(name) and name is not None:
        if isNew:
            entries[name] = {'type': type, 'factory': factory,
                             'isNew': 'Y', 'path': objpath}
        else:
            entries[name] = {'type': type, 'factory': factory, 'path': objpath}
    open(entries_path, 'w').write(dumps(entries))

def getFSRoot(fspath, next=None):
    """Returns the sandbox root.
    """
    fspath = os.path.abspath(fspath)
    if not os.path.exists(os.path.join(fspath,'@@Zope')):
        return os.path.join(fspath,next)
    else:
        return getFSRoot(os.path.dirname(fspath), os.path.basename(fspath))
