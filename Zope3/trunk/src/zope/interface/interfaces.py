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
"""

$Id: interfaces.py,v 1.7 2003/01/31 16:22:01 stevea Exp $
"""

from zope.interface import Interface
from zope.interface.interface import Attribute

class IElement(Interface):
    """Objects that have basic documentation and tagged values.
    """

    __name__ = Attribute('__name__', 'The object name')
    __doc__  = Attribute('__doc__', 'The object doc string')

    def getName():
        """Returns the name of the object."""

    def getDoc():
        """Returns the documentation for the object."""

    def getTaggedValue(tag):
        """Returns the value associated with 'tag'."""

    def getTaggedValueTags():
        """Returns a list of all tags."""

    def setTaggedValue(tag, value):
        """Associates 'value' with 'key'."""



class IAttribute(IElement):
    """Attribute descriptors"""



class IMethod(IAttribute):
    """Method attributes
    """
    # XXX What the heck should methods provide? Grrrr

    def getSignatureString():
        """Return a signature string suitable for inclusion in documentation.
        """

class IInterface(IElement):
    """Interface objects

    Interface objects describe the behavior of an object by containing
    useful information about the object.  This information includes:

      o Prose documentation about the object.  In Python terms, this
        is called the "doc string" of the interface.  In this element,
        you describe how the object works in prose language and any
        other useful information about the object.

      o Descriptions of attributes.  Attribute descriptions include
        the name of the attribute and prose documentation describing
        the attributes usage.

      o Descriptions of methods.  Method descriptions can include:

        o Prose "doc string" documentation about the method and its
          usage.

        o A description of the methods arguments; how many arguments
          are expected, optional arguments and their default values,
          the position or arguments in the signature, whether the
          method accepts arbitrary arguments and whether the method
          accepts arbitrary keyword arguments.

      o Optional tagged data.  Interface objects (and their attributes and
        methods) can have optional, application specific tagged data
        associated with them.  Examples uses for this are examples,
        security assertions, pre/post conditions, and other possible
        information you may want to associate with an Interface or its
        attributes.

    Not all of this information is mandatory.  For example, you may
    only want the methods of your interface to have prose
    documentation and not describe the arguments of the method in
    exact detail.  Interface objects are flexible and let you give or
    take any of these components.

    Interfaces are created with the Python class statement using
    either Interface.Interface or another interface, as in::

      from zope.interface import Interface

      class IMyInterface(Interface):
        '''Interface documentation
        '''

        def meth(arg1, arg2):
            '''Documentation for meth
            '''

        # Note that there is no self argument

     class IMySubInterface(IMyInterface):
        '''Interface documentation
        '''

        def meth2():
            '''Documentation for meth2
            '''

    You use interfaces in two ways:

    o You assert that your object implement the interfaces.

      There are several ways that you can assert that an object
      implements an interface::

      1. Include an '__implements__' attribute in the object's class
         definition. The value of the '__implements__' attribute must
         be an implementation specification. An implementation
         specification is either an interface or a tuple of
         implementation specifications.

      2. Incluse an '__implements__' attribute in the object.
         Because Python classes don't have their own attributes, to
         assert that a class implements interfaces, you must provide a
         '__class_implements__' attribute in the class definition.

         **Important**: A class usually doesn't implement the
           interfaces that its instances implement. The class and
           its instances are separate objects with their own
           interfaces.

      3. Call 'Interface.Implements.implements' to assert that instances
         of a class implement an interface.

         For example::

           from zope.interface.implements import implements

           implements(some_class, some_interface)

         This is approach is useful when it is not an option to modify
         the class source.  Note that this doesn't affect what the
         class itself implements, but only what its instances
         implement.

      4. For types that can't be modified, you can assert that
         instances of the type implement an interface using
         'Interface.Implements.assertTypeImplements'.

         For example::

           from zope.interface.implements import assertTypeImplements

           assertTypeImplements(some_type, some_interface)

    o You query interface meta-data. See the IInterface methods and
      attributes for details.

    """

    def getBases():
        """Return a sequence of the base interfaces."""

    def extends(other, strict=True):
        """Test whether the interface extends another interface

        A true value is returned in the interface extends the other
        interface, and false otherwise.

        Normally, an interface doesn't extend itself. If a false value
        is passed as the second argument, or via the 'strict' keyword
        argument, then a true value will be returned if the interface
        and the other interface are the same.
        """

    def isImplementedBy(object):
        """Test whether the interface is implemented by the object

        Return true of the object asserts that it implements the
        interface, including asseting that it implements an extended
        interface.
        """

    def isImplementedByInstancesOf(class_):
        """Test whether the interface is implemented by instances of the class

        Return true of the class asserts that its instances implement the
        interface, including asseting that they implement an extended
        interface.
        """

    def names(all=False):
        """Get the interface attribute names

        Return a sequence of the names of the attributes, including
        methods, included in the interface definition.

        Normally, only directly defined attributes are included. If
        a true positional or keyword argument is given, then
        attributes defined by nase classes will be included.
        """

    def namesAndDescriptions(all=False):
        """Get the interface attribute names and descriptions

        Return a sequence of the names and descriptions of the
        attributes, including methods, as name-value pairs, included
        in the interface definition.

        Normally, only directly defined attributes are included. If
        a true positional or keyword argument is given, then
        attributes defined by nase classes will be included.
        """

    def getDescriptionFor(name):
        """Get the description for a name

        If the named attribute is not defined, a KeyError is raised.
        """

    __getitem__ = getDescriptionFor

    def queryDescriptionFor(name, default=None):
        """Look up the description for a name

        If the named attribute is not defined, the default is
        returned.
        """

    get = queryDescriptionFor

    def __contains__(name):
        """Test whether the name is defined by the interface"""

    def __iter__():
        """Return an iterator over the names defined by the interface

        The names iterated include all of the names defined by the
        interface directly and indirectly by base interfaces.
        """

class ITypeRegistry(Interface):
    """Type-specific registry

    This registry stores objects registered for objects that implement
    a required interface.
    """

    def register(interface, object):
        """Register an object for an interface.

        The interface argument may be None.  This effectively defines a
        default object.
        """

    def unregister(interface):
        """Remove the registration for the given interface

        If nothing is registered for the interface, the call is ignored.
        """

    def get(interface, default=None):
        """Return the object registered for the given interface.
        """

    def getAll(implements):
        """Get registered objects

        Return a sequence of all objects registered with interfaces
        that are extended by or equal to one or more interfaces in the
        given interface specification.

        """

    def getAllForObject(object):
        """Get all registered objects for types that object implements.
        """

    def getTypesMatching(interface):
        """Get all registered interfaces matching the given interface

        Returns a sequence of all interfaces registered that extend
        or are equal to the given interface.
        """

    def __len__():
        """Returns the number of distinct interfaces registered.
        """

class IAdapterRegistry(Interface):
    """Adapter-style registry

    This registry stores objects registered to convert (or participate
    in the conversion from) one interface to another. The interface
    converted is the "required" interface. We say that the interface
    converted to is the "provided" interface.

    The objects registered here don't need to be adapters. What's
    important is that they are registered according to a required and
    a provided interface.

    The provided interface may not be None.

    The required interface may be None. Adapters with a required
    interface of None adapt non-components. An adapter that adapts all
    components should specify a required interface of
    Interface.Interface.

    """

    def register(require, provide, object):
        """Register an object for a required and provided interface.

        There are no restrictions on what the object might be.
        Any restrictions (e.g. callability, or interface
        implementation) must be enforced by higher-level code.

        The require argument may be None.

        """

    def get((implements, provides), default=None, filter=None):
        """Return a registered object

        The registered object is one that was registered to require an
        interface that one of the interfaces in the 'implements'
        specification argument extends or equals and that provides an
        interface that extends or equals the 'provides' argument.  An
        attempt will be made to find the component that most closely
        matches the input arguments.

        The object returned could have been registred to require None.

        Note that the implements may be None, it which case a
        component will be returned only if it was registered with a
        require of None.

        An optional filter may be provided. If provided, the returned
        object must pass the filter. Search will continue until a
        suitable match can be found. The filter should take a single
        argument and return a true value if the object passes the
        filter, or false otherwise.

        """

    def getForObject(object, interface, filter=None):
        """Get an adapter for object that implements the specified interface

        The filter option has the same meaning as in the get method.
        """

    def getRegistered(require, provide):
        """return data registred specificly for the given interfaces

        None is returned if nothing is registered.
        """

    def getRegisteredMatching(required_interfaces=None,
                              provided_interfaces=None):
        """Return information about registered data

        Zero or more required and provided interfaces may be
        specified. Registration information matching any of the
        specified interfaces is returned.

        The arguments may be interfaces, or sequences of interfaces.

        The returned value is a sequence of three-element tuples:

        - required interface

        - provided interface

        - the object registered specifically for the required and
          provided interfaces.

        To understand how the matching works, imagine that we have
        interfaces R1, R2, P1, and P2. R2 extends R1. P2 extends P1.
        We've registered C to require R1 and provide P2.  Given this,
        if we call getRegisteredMatching:

          registery.getRegisteredMatching([R2], [P1])

        the returned value will include:

          (R1, P2, C)
        """

class IImplementorRegistry(Interface):
    """Implementor registry

    This registry stores objects registered to implement (or help
    implement) an interface. For example, this registry could be used
    to register utilities.

    The objects registered here don't need to be implementors. (They
    might just be useful to implementation.) What's important is that
    they are registered according to a provided interface.

    """

    def register(provide, object):
        """Register an object for a required and provided interface.

        There are no restrictions on what the object might be.
        Any restrictions (e.g. callability, or interface
        implementation) must be enforced by higher-level code.

        The require argument may be None.

        """

    def get(provides, default=None):
        """Return a registered object

        The registered object is one that was registered that provides an
        interface that extends or equals the 'provides' argument.

        """
