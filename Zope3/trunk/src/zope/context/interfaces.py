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

$Id: interfaces.py,v 1.16 2003/06/14 12:32:38 stevea Exp $
"""

from zope.interface import Interface, Attribute

class IWrapperFuncs(Interface):
    """Interface implemented by callables in 'wrapper' module"""

    def Wrapper(object, context=None, **data):
        """Create and return a new context wrapper for object.

        If context is not None, context will be the context object.
        Wrapper can be subclassed.

        Wrapper data may be passed as keyword arguments. The data are
        added to the context dictionary.

        Note that the object and context must be passed as positional
        arguments. All keyword arguments, even those called 'object' and
        'context' are taken as part of data.
        A less informative but more accurate function signature would be

          def Wrapper(*args, **data):

        Where args is either (object,) or (object, context).
        """

    def getinnerwrapper(obj):
        """Return the innermost wrapper.

        Returns the innermost wrapper in a chain of wrappers with obj at the
        head.  If obj is not a wrapper, just return obj.
        """

    def getinnercontext(obj):
        """Return the innermost context.

        Return the context object from the innermost wrapper in a chain with
        obj at the head. If the innermost wrapper has no context object,
        return None. If obj is not a wrapper, return None.
        """

    def getcontext(obj):
        """Return the context object if there is one, otherwise None.

        If obj is not a wrapper instance, return None.
        """

    def getdict(obj):
        """Return the context dictionary if there is one, otherwise None.

        If obj is not a wrapper instance, return None.
        """

    def getdictcreate(wrapper):
        """Return the context dictionary.

        If it does not already exist, the context dictionary will be created.
        Raises TypeError if wrapper is not a wrapper object.
        """

    def setobject(wrapper, object):
        """Replace the wrapped object with the given object.

        Raises TypeError if wrapper is not a wrapper object.
        """

    def setcontext(wrapper, context):
        """Replace the context object with the given context.

        If context is None, it will be represented as NULL in C API. Raises
        TypeError if wrapper is not a wrapper object.
        """


class IWrapper(Interface):
    """A Wrapper is a transparent proxy around an object.

    It provides a place to keep the object's context, in the form of
    a reference to its context object, and a dictionary of contextual metadata.

    If a descriptor on the wrapped object's class is a ContextDescriptor,
    then the 'self' of the method will be rebound to be the wrapper rather
    than the object.
    Rebinding does not work at all if the wrapped object is a Classic Class
    instance.
    Such rebinding is supported for ordinary descriptors, but only for
    the following 'slot descriptors'.

    __len__
    __nonzero__
    __getitem__
    __setitem__
    __delitem__
    __iter__
    next
    __contains__
    __call__
    __str__
    """


class IWrapperIntrospection(Interface):
    """Wrapper API provided to applications."""

    def getWrapperData(ob):
        """Get the context wrapper data for an object"""

    def getInnerWrapperData(ob):
        """Get the inner (container) context wrapper data for an object"""

    def getWrapperContainer(ob):
        """Get the object's container, as computed from a context wrapper.

        This is the context of the innermost wrapper.
        """

    def getWrapperContext(ob):
        """Get the object's context, as computed from a context wrapper.

        This is the context of the outermost wrapper.
        """

    def isWrapper(ob):
        """Returns True if the object is wrapped in a context wrapper.

        Otherwise returns False.
        """

    def ContainmentIterator(ob):
        """Get an iterator for the object's containment chain.

        The iteration starts at ob and proceeds through ob's containers.
        As with getWrapperContainer, the container is the context of the
        innermost wrapper.
        """

    def ContextIterator(ob):
        """Get an iterator for the object's context chain.

        The iteration starts at ob and proceeds through ob's contexts.
        """

class IContextAwareDescriptorSupport(Interface):
    """Special utilities for creating context-aware descriptors 

    A context-aware descriptors is bound to context wrappers, rather than to
    unwrapped instances.
    """

    ContextDescriptor = Attribute(
        """Marker descriptor base class

        Descriptor implementations that subclass this class will have
        wrappers passed to their descriptor methods if they are
        accessed through wrapped objects.
        """)

    def ContextMethod(method):
        """Convert ordinary methods to context-aware methods.

        The first argument passed to methods will be context wrapped
        if the method is called on a context-wrapped instance.
        """

    def ContextProperty(fget, fset=None, fdel=None):
        """\
        Create a property with functions to be passed context-wrapped instances

        This function works like Python's property function, except
        that the access functions are passed context-wrapped instances.
        """

    def ContextSuper(cls, wrapped_instance):
        """Call an inherited method on a wrapped instances
        """

    def ContextAwareDescriptors():
        """Function used in a class suite to advise use of context descriptors

        All descriptors defined in that class suite will be made
        context-aware.
        """
