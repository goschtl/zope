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

import string, os, commands

from common import getZODBPath, createTempfile, getObject
from common import mapFS, traverseFS, checkConflictData, getApplicationRoot
from common import isNewObject, getFSRoot, setPrint

from zope.app.fssync.syncer import toFS

env = os.environ

def update(fspath
           , dbpath
           , siteconfpath):
    """Updates the checked out objects in the file system from a ZODB

    updates the files in the sandbox based on the file system path given
    by -f option.
    """
    root = getApplicationRoot(dbpath, siteconfpath)
    if env.has_key('SYNCROOT'):
        if os.path.abspath(fspath) == os.path.abspath(env['SYNCROOT']):
            if os.path.isdir(os.path.abspath(fspath)):
                module_list = os.listdir(os.path.abspath(fspath))
                if '@@Zope' in module_list:
                    module_list.remove('@@Zope')
                    for module in module_list:
                        fspath = os.path.join(fspath, module)
                        updateSettings(fspath, root)
                else:
                    return 'sync [update aborted] : @@Zope administrative folder not found in %s' \
                           %(fspath)
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
        return 'sync [update aborted] : @@Zope administrative folder not found in %s'\
               %(fspath)

    mappings = {}
    mapping_paths = {}
    mapping_paths.update(traverseFS(fspath, mapping_paths))

    for sandbox_path in mapping_paths.keys():
        original_path = string.strip(mapping_paths[sandbox_path][0])
        zopedb_path = string.strip(mapping_paths[sandbox_path][1])
        if checkConflictData(sandbox_path, zopedb_path):
            setPrint('C %s'%(zopedb_path[1:]))
        else:
            if not isNewObject(sandbox_path):
                mappings[zopedb_path] = sandbox_path

                fmt_sandbox_path = ''
                fmt_original_path = ''
                for dir in string.split(sandbox_path,os.sep):
                    if string.find(dir, ' ')<>-1:
                        fmt_sandbox_path = os.path.join(fmt_sandbox_path, '\''+dir+'\'')
                    else:
                        fmt_sandbox_path = os.path.join(fmt_sandbox_path, dir)

                for dir in string.split(original_path,os.sep):
                    if string.find(dir, ' ')<>-1:
                        fmt_original_path = os.path.join(fmt_original_path, '\''+dir+'\'')
                    else:
                        fmt_original_path = os.path.join(fmt_original_path, dir)
                fmt_sandbox_path = os.sep + fmt_sandbox_path
                fmt_original_path = os.sep + fmt_original_path

                ob = getObject(zopedb_path, root)
                zopedb_temp_file = createTempfile(ob, zopedb_path)
                diff3_cmd = """diff3 -a %s %s %s""" %(fmt_sandbox_path
                                                      , fmt_original_path
                                                      , zopedb_temp_file)
                diff3_res = commands.getoutput(diff3_cmd)
                if len(string.strip(diff3_res))>1:
                    diffverify=string.strip(diff3_res[0:5])
                    if diffverify=='====1':
                        setPrint('M %s'%(zopedb_path[1:]))
                    elif diffverify=='====2':
                        doUpdate('C', ob, zopedb_path, sandbox_path)
                        setPrint('M %s'%(zopedb_path[1:]))
                    elif diffverify=='====3':
                        doUpdate('U', ob, zopedb_path, sandbox_path)
                    elif diffverify=='====':
                        diff3_cmd = """diff3 -a -m %s %s %s;echo $?""" %(fmt_sandbox_path
                                                                         , fmt_original_path
                                                                         , zopedb_temp_file)
                        diff3_res = commands.getoutput(diff3_cmd)
                        diff3_res = string.replace(diff3_res
                                                   , zopedb_temp_file
                                                   , zopedb_path)
                        if diff3_res[-1]=='0':
                            setPrint('Merging changes in %s' \
                                     %(zopedb_path[1:]))
                        else:
                            setPrint('C Merging changes in %s' \
                                     %(zopedb_path[1:]))

                        f = open(sandbox_path, 'w')
                        f.write(string.strip(diff3_res[:-1]))
                        f.close()
                        doUpdate('C'
                                 , ob
                                 , zopedb_path
                                 , sandbox_path)

                if os.path.exists(zopedb_temp_file):
                    os.remove(zopedb_temp_file)

    if os.path.isdir(fspath):
        objectroot = getZODBPath(fspath)
        fsroot = getFSRoot(fspath)
        mapFS(mappings
              , root
              , objectroot
              , fsroot)



def doUpdate(mode
             , ob
             , zopedb_path
             , sandbox_path):
    """Updates data
    """
    sandbox_path = os.path.dirname(sandbox_path)
    ob_name = string.split(zopedb_path,'/')[-1]
    if mode=='U':
        if ob is not None:
            toFS(ob, ob_name, sandbox_path)
    elif mode=='C':
        if ob is not None:
            toFS(ob, ob_name, sandbox_path, mode)
