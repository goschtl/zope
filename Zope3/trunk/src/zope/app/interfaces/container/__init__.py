#
# This file is necessary to make this directory a package.


from zope.interface import Interface, Attribute
from zope.component.interfaces import IView
from zope.interface.common.mapping import IItemMapping
from zope.interface.common.mapping import IReadMapping, IEnumerableMapping

class DuplicateIDError(KeyError):
    pass

class ContainerError(Exception):
    """An error of a container with one of its components."""


class UnaddableError(ContainerError):
    """An object cannot be added to a container."""

    def __init__(self, container, obj, message=""):
        self.container = container
        self.obj = obj
        self.message = message and ": %s" % message

    def __str__(self):
        return ("%(obj)s cannot be added "
                "to %(container)s%(message)s" % self.__dict__)


class IItemContainer(IItemMapping):
    """Minimal readable container
    """

class ISimpleReadContainer(IItemContainer, IReadMapping):
    """Readable content containers
    """

class IReadContainer(ISimpleReadContainer, IEnumerableMapping):
    """Readable containers that can be enumerated.
    """

class IWriteContainer(Interface):
    """An interface for the write aspects of a container."""

    def setObject(key, object):
        """Add the given object to the container under the given key.

        Raises a ValueError if key is an empty string, unless the
        container chooses a different key.

        Raises a TypeError if the key is not a unicode or ascii string.

        Returns the key used, which might be different than the given key.
        """

    def __delitem__(key):
        """Delete the keyed object from the container.

        Raises a KeyError if the object is not found.
        """

class IContentContainer(IWriteContainer):
    """Containers (like folders) that contain ordinary content"""

class IContainer(IReadContainer, IWriteContainer):
    """Readable and writable content container."""

class IOptionalNamesContainer(IContainer):
    """Containers that will choose names for their items if no names are given
    """

class IContainerNamesContainer(IContainer):
    """Containers that always choose names for their items
    """



class IAdding(IView):

    def add(content):
        """Add content object to container.

        Add using the name in contentName.  Returns the added object
        in the context of its container.

        If contentName is already used in container, raises
        DuplicateIDError.
        """

    contentName = Attribute(
         """The content name, as usually set by the Adder traverser.

         If the content name hasn't been defined yet, returns None.

         Some creation views might use this to optionally display the
         name on forms.
         """
         )

    def nextURL():
        """Return the URL that the creation view should redirect to.

        This is called by the creation view after calling add.

        It is the adder's responsibility, not the creation view's to
        decide what page to display after content is added.
        """

class IZopeItemContainer(IItemContainer):

    def __getitem__(key):
        """Return the content for the given key

        Raises KeyError if the content can't be found.

        The returned value will be in the context of the container.
        """


class IZopeSimpleReadContainer(IZopeItemContainer, ISimpleReadContainer):
    """Readable content containers
    """

    def get(key, default=None):
        """Get a value for a key

        The default is returned if there is no value for the key.

        The value for the key will be in the context of the container.
        """


class IZopeReadContainer(IZopeSimpleReadContainer, IReadContainer):
    """Readable containers that can be enumerated.
    """


    def values():
        """Return the values of the mapping object in the context of
           the container
        """

    def items():
        """Return the items of the mapping object in the context
           of the container
        """


class IZopeWriteContainer(IWriteContainer):
    """An interface for the write aspects of a container."""

    def setObject(key, object):
        """Add the given object to the container under the given key.

        Raises a ValueError if key is an empty string, unless the
        context wrapper chooses a different key.

        Returns the key used, which might be different than the given key.

        If the object has an adpter to IAddNotifiable then the manageAfterAdd
        method on the adpter will be called after the object is added.

        An IObjectAddedEvent will be published after the object is added and
        after manageAfterAdd is called. The event object will be the added
        object in the context of the container

        An IObjectModifiedEvent will be published after the IObjectAddedEvent
        is published. The event object will be the container.
        """

    def __delitem__(key):
        """Delete the keyd object from the context of the container.

        Raises a KeyError if the object is not found.

        If the object has an adpter to IDeleteNotifiable then the
        manageBeforeDeleteObject method on the adpter will be called before
        the object is removed.

        An IObjectRemovedEvent will be published before the object is
        removed and before  manageBeforeDeleteObject is called.
        The event object will be the removed from the context of the container

        An IObjectModifiedEvent will be published after the
        IObjectRemovedEvent is published. The event object will be the
        container.
        """

class IZopeContainer(IZopeReadContainer, IZopeWriteContainer, IContainer):
    """Readable and writable content container."""

class IAddNotifiable(Interface):
    """Interface for notification of being added."""

    def manage_afterAdd(object, container):
        """Hook method will call after an object is added to container."""

class IDeleteNotifiable(Interface):
    """Interface for notification of being deleted."""

    def manage_beforeDelete(object, container):
        """Hook method will call before object is removed from container."""

class IMoveNotifiable(IDeleteNotifiable, IAddNotifiable):
    """Interface for notification of being deleted, added, or moved."""

    def manage_beforeDelete(object, container, movingTo=None):
        """Hook method will call before object is removed from container.

        If the object is being moved, 'movingTo' will be the unicode path
        the object is being moved to.
        If the object is simply being deleted and not being moved, 'movingTo'
        will be None.
        """

    def manage_afterAdd(object, container, movedFrom=None):
        """Hook method will call after an object is added to container.

        If the object is being moved, 'movedFrom' will be the unicode path
        the object was moved from.
        If the object is simply being added and not being moved, 'movedFrom'
        will be None.
        """

class ICopyNotifiable(IAddNotifiable):
    def manage_afterAdd(object, container, copiedFrom=None):
        """Hook method. Will be called after an object is added to a
        container.

        If the object is being copied, 'copiedFrom' will
        be the unicode path the object was copied from.

        If the object is simply being added and not being copied,
        'copiedFrom' will be None.
        
        Clients calling this method must be careful to use
        'copiededFrom' as a keyword argument rather than a positional
        argument, to avoid confusion if the object is both
        IMoveNotifiable and ICopyNotifiable.  """

class IPasteTarget(Interface):
    
    def acceptsObject(key, obj):
        '''Allow the container to say if it accepts the given wrapped
        object.
        
        Returns True if the object would be accepted as contents of
        this container. Otherwise, returns False.
        '''

    def pasteObject(key, obj):
        '''Add the given object to the container under the given key.
        
        Raises a ValueError if key is an empty string, unless the
        this object chooses a different key.
        
        Returns the key used, which might be different than the
        given key.
        
        This method must not issue an IObjectAddedEvent, nor must it
        call the manage_afterAdd hook of the object.
        However, it must publish an IObjectModified event for the
        container.
        '''

class IMoveSource(Interface):

    def removeObject(key, movingTo):
        '''Remove and return the object with the given key, as the
        first part of a move.

        movingTo is the unicode path for where the move is to.
        This method should not publish an IObjectRemovedEvent, nor should  
        it call the manage_afterDelete method of the object.
        However, it must publish an IObjectModified event for the container.
        '''

class ICopySource(Interface):
    
    def copyObject(key, copyingTo):
        '''Return the object with the given key, as the first part of a
        copy.

        copyingTo is the unicode path for where the copy is to.
        '''

class IContainerCopyPasteMoveSupport(ICopySource, IPasteTarget, IMoveSource):
    '''An interface for containers that support copy,
    paste and move operations'''
    
