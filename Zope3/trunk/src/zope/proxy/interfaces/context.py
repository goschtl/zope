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

$Id: context.py,v 1.8 2003/05/09 14:02:56 stevea Exp $
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

    def getobject(obj):
        """Return the wrapped object.

        If obj is not a wrapper object, return obj.
        """

    def getbaseobject(obj):
        """Return the innermost wrapped object.

        If obj is not a wrapper, return obj.
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

    If the wrapped object's class derives from ContextAware, or a descriptor
    on the wrapped object's class is a ContextDescriptor, then the 'self'
    of the method will be rebound to be the wrapper rather than the object.
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

    def __getstate__():
        """Raises AttributeError if called (to prevent pickling)"""


class IDecoratorFuncs(Interface):
    """Interface implemented by callables in 'decorator' module"""

    def Decorator(object, context=None, mixinfactory=None, names=(),
                  attrdict={}, **data):
        """Create and return a new decorator for object.

        Decorator is a subtype of Wrapper.

        If context is not None, context will be the context object.

        If mixinfactory is not None, mixinfactory is a callable that need
        take no arguments for creating the decorator mixin.

        'names' is a tuple of names that are dispatched to the mixin rather
        than to the object. The mixin is instantiated from the factory
        before the first dispatch of one of the names.
        If names is passed in with a None value, it is the same as ().

        'attrdict' is a dict of name:value. Values may take any value
        including None. If an attribute with a name in 'attrdict' is
        sought from the decorator, the value from the attrdict will be
        returned. Attempting to setattr or delattr with this name results in
        an AttributeError. If attrdict is passed in with a None value, it is
        the same as {}.

        If the same name appears in names and in attrdict, the behaviour is
        as if the name appeared only in attrdict.

        Wrapper data may be passed as keyword arguments. The data are added
        to the context dictionary.

        Note that the arguments object, context, mixinfactory, names, and
        attrdict must be given as positional arguments. All keyword arguments
        are taken to be part of **data.
        """

    def getmixin(obj):
        """Returns the mixin object.

        Returns None if the mixin is not instantiated.
        """

    def getmixinfactory(obj):
        """Returns the mixin factory."""

    def getnames(obj):
        """Returns the tuple of names."""

    def getnamesdict(obj):
        """Returns a read-only dict used for fast lookup of names.

        This method is provided so that unit-tests can check that the
        dict is created properly. It should otherwise be considered
        a private API.
        """

class IDecorator(IWrapper):
    """A Decorator is a subtype of Wrapper.

    In addition to the description in IWrapper's docstring, a decorator
    dispatches certain names to a separate "mixin" instance, rather than
    to the wrapped object.
    """


class IDecoratorMixinFactory(Interface):
    """The callable that creates a mixin.
    """
    def __call__(inner, outer):
        """Create a new mixin instance.

        inner is the object being decorated.
        outer is the decorator wrapper.
        """

class IDecoratorMixinEnvironment(Interface):
    """The attributes that an instantiated mixin can expect to have available.

    In a mixin, the 'self' of a method is always the normal unwrapped
    self of the mixin instance. ContextMethods and other ContextDescriptors
    will work, but should not be necessary.

    When the mixin needs context, for example for using a local service,
    it can use self.outer.
    self.inner is a shortcut for getobject(self.outer).

    This is the application api for writing simple decorator classes.
    """

    inner = Attribute('The object that is being decorated')
    outer = Attribute('The Decorator instance')


class IContextWrapper(Interface):
    """Wrapper API provided to applications."""

    def ContextWrapper(object, parent, **data):
        """Create a context wrapper for object in parent

        If the object is in a security proxy, then result will be
        a security proxy for the unproxied object in context.

        Consider an object, o1, in a proxy p1 with a checker c1.

        If we call ContextWrapper(p1, parent, name='foo'), then we'll
        get::

          Proxy(Wrapper(o1, parent, name='foo'), c1)
        """

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

class IContextDecorator(IContextWrapper):
    """Wrapper and Decorator API provided to applications."""

    def ContextWrapper(object, parent, **data):
        """Create a context wrapper for object in parent

        If the object is in a security proxy, then result will be
        a security proxy for the unproxied object in context.

        The object is examined to see if it should be wrapped with
        a Wrapper or with a Decorator. How this is done is up to the
        implementation.
        """

