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
"""Filesystem synchronization classes.

$Id: classes.py,v 1.2 2003/05/05 18:01:01 gvanrossum Exp $
"""

import os

from zope.app.content.file import File
from zope.app.content.folder import Folder
from zope.app.interfaces.fssync import IFSAddView, IObjectFile
from zope.component.interfaces import IPresentationRequest
from zope.xmlpickle.xmlpickle import dumps

class FSAddView(object):
    """See IFSAddView."""

    __implements__ = IFSAddView

    def __init__(self, context, request):
        self.context = context
        self.request = request

class AddView(FSAddView):
    """Supports to create a file system representation of zope
       file type objects
    """

    def create(self, fs_path=None):
        if os.path.isdir(fs_path):
            return Folder()
        else:
            return File()

class AttrMapping(object):
    """Convenience object implementing a mapping on selected object attributes
    """

    def __init__(self, context, attrs, schema=None):
        self.attrs = attrs
        self.context = context

    def __getitem__(self, name):
        if name in self.attrs:
            return getattr(self.context, name)
        raise KeyError, name

    def get(self, name, default):
        if name in self.attrs:
            return getattr(self.context, name, default)
        return default

    def __contains__(self, name):
        return (name in self.attrs) and hasattr(self.context, name)

    def __delitem__(self, name):
        if name in self.attrs:
            delattr(self.context, name)
            return
        raise KeyError, name

    def __setitem__(self, name, value):
        if name in self.attrs:
            setattr(self.context, name, value)
            return
        raise KeyError, name

    def __iter__(self):
        return iter(self.attrs)

class ObjectEntryAdapter(object):
    """Convenience Base class for ObjectEntry adapter implementations."""

    def __init__(self, context):
        self.context = context

    def extra(self):
        "See Zope.App.FSSync.IObjectEntry.IObjectEntry"

    def typeIdentifier(self):
        "See Zope.App.FSSync.IObjectEntry.IObjectEntry"
        class_ = self.context.__class__
        return "%s.%s" % (class_.__module__, class_.__name__)

    def factory(self):
        "See Zope.App.FSSync.IObjectEntry.IObjectEntry"
        # Return the dotted class name, assuming that it can be used
        class_ = self.context.__class__
        return "%s.%s" % (class_.__module__, class_.__name__)

class Default(ObjectEntryAdapter):
    """Default File-system representation for objects."""

    __implements__ =  IObjectFile

    def getBody(self):
        "See IObjectFile"
        if type(self.context) is str:
            return self.context
        return dumps(self.context)

    def setBody(self, body):
        pass

    def factory(self):
        "See IObjectEntry"
        # We have no factory, cause we're a pickle.
        return None

class FSAddRequest(object):
    """XXX docstring???"""

    __implements__ = IPresentationRequest

    def getPresentationType(self):
        return IFSAddView

    def getPresentationSkin(self):
        return 'default'
