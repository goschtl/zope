##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Filesystem synchronization classes.

$Id$
"""

from zope.fssync.server.interfaces import IObjectFile, IContentDirectory
from zope.interface import implements
from zope.xmlpickle import toxml

# TODO: This is a bug; we shouldn't depend on these packages at all.
# Need to restructure.
from zope.proxy import removeAllProxies
from zope.app.fssync import fspickle

class AttrMapping(object):
    """Convenience object implementing a mapping on selected object attributes
    """

    def __init__(self, context, attrs):
        self.attrs = attrs
        self.context = context

    def __getitem__(self, name):
        if name in self.attrs:
            return getattr(self.context, name)
        raise KeyError, name

    def get(self, name, default=None):
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
        "See IObjectEntry"
        return None

    def typeIdentifier(self):
        "See IObjectEntry"
        class_ = self.context.__class__
        return "%s.%s" % (class_.__module__, class_.__name__)

    def factory(self):
        "See IObjectEntry"
        # Return the dotted class name, assuming that it can be used
        class_ = self.context.__class__
        return "%s.%s" % (class_.__module__, class_.__name__)

class DefaultFileAdpater(ObjectEntryAdapter):
    """Default File-system representation for objects."""

    implements(IObjectFile)

    def __init__(self, context):
        # TODO: for now, remove all proxies.
        ObjectEntryAdapter.__init__(self, removeAllProxies(context))

    def getBody(self):
        "See IObjectFile"
        s = fspickle.dumps(self.context)
        return toxml(s)

    def setBody(self, body):
        "See IObjectFile"
        raise NotImplementedError

    def factory(self):
        "See IObjectEntry"
        # We have no factory, cause we're a pickle.
        return None

    def annotations(self):
        # The annotations are already stored in the pickle.
        # This is only the right thing if the annotations are
        # stored in the object's attributes (such as IAttributeAnnotatable);
        # if that's not the case, then either this method needs to be
        # overridden or this class shouldn't be used.
        return None

class DirectoryAdapter(ObjectEntryAdapter):
    """Folder adapter to provide a file-system representation.
    """
    implements(IContentDirectory)

    def contents(self):
        result = []
        for name, object in self.context.items():
            result.append((name, object))
        return result
