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
"""Interfaces related to context wrappers.

$Id: interfaces.py,v 1.2 2002/12/25 14:15:17 jim Exp $
"""

from zope.interface import Interface

class IWrapperFuncs(Interface):
    """ Interface implemented by callables in 'wrapper' module """
    def Wrapper(object, context=None, **data):
        """
        Create and return a new context wrapper for object. If context is given
        and not None, context will be the context object. Wrapper can be
        subclassed.

        Wrapper data may be passed as keyword arguments. The data are
        added to the context dictionary.
        """

    def getobject(obj):
        """
        Return the wrapped object. If obj is not a wrapper object, return obj.
        """
    def getbaseobject(obj):
        """
        Return the innermost wrapped object.  If obj is not a wrapper,
        return obj.
        """
    def getinnerwrapper(obj):
        """
        Return the innermost wrapper in a chain of wrappers with obj at the
        head. If obj is wrapped, just return obj.
        """
    def getinnercontext(obj):
        """
        Return the context object from the innermost wrapper in a chain with
        obj at the head. If the innermost wrapper has not context object,
        return None. If obj is not a wrapper, return None.
        """
    def getcontext(obj):
        """
        Return the context object if there is one, or None. If obj is not a
        wrapper instance, return None.
        """
    def getdict(obj):
        """
        Return the context dictionary if there is one, or None. If obj is not a
        wrapper instance, return None.
        """
    def getdictcreate(wrapper):
        """
        Return the context dictionary, creating it if it does not already
        exist. Raises TypeError if wrapper is not a wrapper object.
        """
    def setobject(wrapper, object):
        """
        Replace the wrapped object with object. Raises TypeError if wrapper is
        not a wrapper object.
        """
    def setcontext(wrapper, context):
        """
        Replace the context object with context. If context is None, it will be
        represented as NULL in C API. Raises TypeError if wrapper is not
        a wrapper object.
        """

class IWrapper(Interface):
    def __getstate__():
        """ Raises AttributeError if called (to prevent pickling) """

class IContextWrapper(Interface):

    def ContextWrapper(object, parent, **data):
        """Create a context wrapper for object in parent

        If the object is in a security proxy, then result will will be
        a security proxy for the unproxied object in context.

        Consider an object, o1, in a proxy p1 with a checker c1.

        If we call ContextWrapper(p1, parent, name='foo'), then we'll
        get::

          Proxy(Wrapper(o1, parent, name='foo'), c1)

        """

    def getWrapperData(ob):
        """Get the context wrapper data for an object
        """

    def getInnerWrapperData(ob):
        """Get the inner (container) context wrapper data for an object
        """

    def getWrapperContainer(ob):
        """Get the object's container, as computed from a context wrapper
        """

    def getWrapperContext(ob):
        """Get the object's context, as computed from a context wrapper
        """

    def isWrapper(ob):
        """If the object is wrapped in a context wrapper, returns true,
        otherwise returns false.
        """

    def ContainmentIterator(ob):
        """Get an iterator for the object's containment chain
        """
