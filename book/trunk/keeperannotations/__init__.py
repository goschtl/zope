##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Implementation of an Annotation Keeper Adapter

$Id$
"""
from BTrees.OOBTree import OOBTree

from zope.interface import implements
from zope.proxy import removeAllProxies

from zope.app import zapi
from zope.app.annotation.interfaces import IAnnotations

from interfaces import IKeeperAnnotatable, IAnnotationKeeper

keeper_key = 'book.keeperannotation.KeeperAnnotations'
  
tmp = {}
  
class KeeperAnnotations(object):
    """Store the annotations in a keeper.
    >>> from zope.interface import directlyProvides
    >>> from zope.app.dublincore.interfaces import IZopeDublinCore
    >>> import datetime
    
    Tell the File class that its instances implement IKeeperAnnotable 
  
    >>> from zope.app.file import File
    >>> file = File()
    >>> directlyProvides(file, IKeeperAnnotatable)
    >>> dc = IZopeDublinCore(file)
    >>> dc.created = dc.modified = datetime.datetime(2004, 01, 01, 12, 00)
    >>> dc_data = tmp[file]['zope.app.dublincore.ZopeDublinCore']
    >>> dc_data[u'Date.Created'][0]
    u'2004-01-01T12:00:00'
    >>> dc_data[u'Date.Modified'][0]
    u'2004-01-01T12:00:00'
  
    Let's make the RootFolder the annotation keeper
  
    >>> from zope.app.folder.interfaces import IRootFolder
    >>> from zope.app.folder import Folder
    >>> root = Folder()
    >>> directlyProvides(root, IAnnotationKeeper, IRootFolder)
  
    Now we need to build up a simple tree
  
    >>> root['folder1'] = Folder()
    >>> root['folder1']['file'] = file
    >>> file = root['folder1']['file']
  
    Next we would like to store some DC data in the file
      
    >>> dc = IZopeDublinCore(file)
    >>> dc.title = u'File Title'
    >>> dc.description = u'This is a file'
      
    This is the moment; let's see where the annotation was stored.
      
    >>> ann = root.__annotations__[keeper_key][file]
    >>> dc_ann = ann['zope.app.dublincore.ZopeDublinCore']
    >>> dc_ann[u'Title'][0]
    u'File Title'
    >>> dc_ann[u'Description'][0]
    u'This is a file'
    >>> dc_ann[u'Date.Created'][0]
    u'2004-01-01T12:00:00'
    >>> dc_ann[u'Date.Modified'][0]
    u'2004-01-01T12:00:00'
  
    Make sure the temporary entries have been removed
  
    >>> tmp
    {}
    """
    implements(IAnnotations)
    __used_for__ = IKeeperAnnotatable
    
    def __init__(self, obj):
        self.obj = obj
        self.obj_key = removeAllProxies(obj)
        self.keeper_annotations = None
        
        # Annotations might be set when object has no context
        if not hasattr(obj, '__parent__') or obj.__parent__ is None:
            self.keeper_annotations = tmp
            return
        
        for parent in zapi.getParents(obj):
            if IAnnotationKeeper.providedBy(parent):
                # We found the keeper, get the annotation that will store
                # the data.
                annotations = IAnnotations(parent)
                if not annotations.has_key(keeper_key):
                    annotations[keeper_key] = OOBTree()
                self.keeper_annotations = annotations[keeper_key]
                    
        if self.keeper_annotations == None:
            raise ValueError, 'No annotation keeper found.'
  
        # There are some temporary stored annotations; add them to the keeper
        if tmp.has_key(obj):
            self.keeper_annotations[self.obj_key] = tmp[obj]
            del tmp[obj]
                
    def __getitem__(self, key):
        """See zope.app.annotation.interfaces.IAnnotations"""
        annotations = self.keeper_annotations.get(self.obj_key, {})
        return annotations[key]
  
    def __setitem__(self, key, value):
        """See zope.app.annotation.interfaces.IAnnotations"""
        if not self.keeper_annotations.has_key(self.obj_key):
            self.keeper_annotations[self.obj_key] = OOBTree()
        self.keeper_annotations[self.obj_key][key] = value
  
    def get(self, key, default=None):
        """See zope.app.annotation.interfaces.IAnnotations"""
        try:
            return self[key]
        except KeyError:
            return default
  
    def __delitem__(self, key):
        """See zope.app.annotation.interfaces.IAnnotations"""
        del self.keeper_annotations[self.obj_key][key]
