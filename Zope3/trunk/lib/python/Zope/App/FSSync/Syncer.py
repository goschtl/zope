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
"""XXX short summary goes here.

XXX longer description goes here.

$Id: Syncer.py,v 1.2 2002/10/11 06:28:05 jim Exp $
"""
__metaclass__ = type

import os
from Zope.ComponentArchitecture import getAdapter, queryAdapter
from Zope.XMLPickle.XMLPickle import dumps, loads
from IObjectEntry import IObjectEntry
from IObjectDirectory import IObjectDirectory
from IObjectFile import IObjectFile
from Zope.App.OFS.Annotation.IAnnotations import IAnnotations
from Zope.App.OFS.Container.IContainer import IContainer
from Zope.Configuration.name import resolve
from Default import Default

def toFS(ob, name, location):
    """Check an object out to the file system

    ob -- The object to be checked out

    name -- The name of the object

    location -- The directory on the file system where the object will go
    """

    # Look for location admin dir
    admin_dir = os.path.join(location, '@@Zope')
    if not os.path.exists(admin_dir):
        os.mkdir(admin_dir)
    
    # Open Entries file
    entries_path = os.path.join(admin_dir, "Entries.xml")
    if os.path.exists(entries_path):
        entries = loads(open(entries_path).read())
    else:
        entries = {}

    # Get the object adapter
    adapter = getAdapter(ob, IObjectEntry)

    entries[name] = {'type': adapter.typeIdentifier(),
                     'factory': adapter.factory(),
                     }

    # Write entries file
    open(entries_path, 'w').write(dumps(entries))


    # Get name path and check that name is not an absolute path
    path = os.path.join(location, name)
    if path == name:
        raise ValueError("Invalid absolute path name")
    

    # Handle extras
    extra = adapter.extra()
    if extra:
        extra_dir = os.path.join(admin_dir, 'Extra')
        if not os.path.exists(extra_dir):
            os.mkdir(extra_dir)
        extra_dir = os.path.join(extra_dir, name)
        if not os.path.exists(extra_dir):
            os.mkdir(extra_dir)
        for ename in extra:
            edata = extra[ename]
            toFS(edata, ename, extra_dir)

    # Handle annotations
    annotations = queryAdapter(ob, IAnnotations)
    if annotations is not None:
        annotation_dir = os.path.join(admin_dir, 'Annotations')
        if not os.path.exists(annotation_dir):
            os.mkdir(annotation_dir)
        annotation_dir = os.path.join(annotation_dir, name)
        if not os.path.exists(annotation_dir):
            os.mkdir(annotation_dir)
        for key in annotations:
            annotation = annotations[key]
            toFS(annotation, key, annotation_dir)
        

    # Handle data
    if IObjectFile.isImplementedBy(adapter):
        open(path, 'w').write(adapter.getBody())
        original_path = os.path.join(admin_dir, 'Original')
        if not os.path.exists(original_path):
            os.mkdir(original_path)
        original_path = os.path.join(original_path, name)
        open(original_path, 'w').write(adapter.getBody())
        

    else:
        # Directory
        if os.path.exists(path):
            dir_entries = os.path.join(path, '@@Zope', 'Entries.xml')
            if os.path.exists(dir_entries):
                open(dir_entries, 'w').write(dumps({}))
        else:
            os.mkdir(path)
            
        
        for cname, cob in  adapter.contents():
            toFS(cob, cname, path)
        
class SynchronizationError(Exception): pass

def _setItem(container, name, ob, old=0):
    # Set an item in a container or in a mapping
    if IContainer.isImplementedBy(container):
        if old:
            del container[name]
        newName = container.setObject(name, ob)
        if newName != name:
            raise SynchronizationError(
                "Container generated new name for %s" % path)
    else:
        # Not a container, must be a mapping
        container[name] = ob

def fromFS(container, name, location):
    """Synchromize a file from what's on the file system.
    """

    # Look for location admin dir
    admin_dir = os.path.join(location, '@@Zope')
    if not os.path.exists(admin_dir):
        raise SynchronizationError("No @@Zope admin directory, %s" % admin_dir)
        
    # Open Entries file
    entries_path = os.path.join(admin_dir, "Entries.xml")
    entries = loads(open(entries_path).read())
    entry = entries[name]
    factory = entry.get('factory')

    # Get name path and check that name is not an absolute path
    path = os.path.join(location, name)
    if path == name:
        raise ValueError("Invalid absolute path name")

    # See if this is an existing object
    if name in container:
        # Yup, let's see if we have the same kind of object
    
        # Get the object adapter
        adapter = getAdapter(container[name], IObjectEntry)
        
        # Replace the object if the type is different
        if adapter.typeIdentifier() != entry.get('type'):
            # We have a different object, replace the one that's there

            if factory:            
                newOb = resolve(factory)()
            else:
                newOb = loads(open(path).read())

            _setItem(container, name, newOb, old=1)

        elif not factory:
            # Special case pickle data
            oldOb = container[name]
            newOb = loads(open(path).read())
            try:
                # See id we can amd should just copy the state
                oldOb._p_oid # Is it persisteny
                getstate = newOb.__getstate__
            except AttributeError:
                # Nope, we have to replace.
                _setItem(container, name, newOb, old=1)
            else:
                oldOb.__setstate__(getstate())
                oldOb._p_changed = 1
                

    else:
        # We need to create a new object

        if factory:            
            newOb = resolve(entry['factory'])()
        else:
            newOb = loads(open(path).read())

        _setItem(container, name, newOb)
        

    # Get the object adapter again
    ob = container[name]
    adapter = getAdapter(ob, IObjectEntry)
    

    # Handle extra
    extra = adapter.extra()
    extra_dir = os.path.join(admin_dir, 'Extra', name)
    extra_entries_path = os.path.join(extra_dir, "@@Zope", "Entries.xml")
    if extra:
        if not os.path.exists(extra_entries_path):
            # The file system has no extras, so delete all of the object's
            # extras.
            for key in extra:
                del extra[key]
        else:
            extra_entries = loads(
                open(extra_entries_path).read())
            for ename in extra_entries:
                fromFS(extra, ename, extra_dir)
    elif os.path.exists(extra_entries_path):
        extra_entries = loads(
            open(extra_entries_path).read())
        if extra_entries:
            raise SynchronizationError(
                "File-system extras for object with no extra data")
    

    # Handle annotations
    annotations = queryAdapter(ob, IAnnotations)
    annotation_dir = os.path.join(admin_dir, 'Annotations', name)
    annotation_entries_path = os.path.join(
        annotation_dir, "@@Zope", "Entries.xml")
    if annotations is not None:
        if not os.path.exists(annotation_entries_path):
            # The file system has no annotations, so delete all of the object's
            # annotations.
            for key in annotations:
                del annotations[key]
        else:
            annotation_entries = loads(
                open(annotation_entries_path).read())
            for ename in annotation_entries:
                fromFS(annotations, ename, annotation_dir)
    elif os.path.exists(annotation_entries_path):
        annotation_entries = loads(
            open(annotation_entries_path).read())
        if annotation_entries:
            raise SynchronizationError(
                "File-system annotations for non annotatable object")

    # Handle data
    if IObjectFile.isImplementedBy(adapter):
        # File
        if os.path.isdir(path):
            raise SynchronizationError("Object is file, but data is directory")
        adapter.setBody(open(path).read())

    else:
        # Directory
        if not os.path.isdir(path):
            raise SynchronizationError("Object is directory, but data is file")

        dir_entries_path = os.path.join(path, '@@Zope', 'Entries.xml')
        dir_entries = loads(open(dir_entries_path).read())

        for cname in dir_entries:
            fromFS(ob, cname, path)
    
    
        
