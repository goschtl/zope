##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Copy and Move support

XXX The theory is unclear about whether copy and move are about
    containers or not.  Many of the relevent interfaces are in
    zope.app.interfaces.container, even though they are supposed not
    to be indepenent of IContainer.

    Perhaps we should just say that this is about containers and move
    these interfaces there.


Problem

  Zope 3 needs to support three kinds of cut/copy/paste behaviour.

  * Renaming an object to a different name in the same container.

  * Moving an object from one place to another.

  * Copying an object to another place.

  The design for this needs to provide the right capabilities and
  introspection to the user-interface. The appropriate events need
  to be issued. The appropriate hooks, such as IDeleteNotifiable,
  need to be called.


Approach

  Events and hooks

    First, I need to explain events and hooks.

    When an object is added to a container, if the object has an
    IAddNotifiable adapter, that adapter's 'manage_afterAdd' method
    is called. Then, an IObjectAddedEvent is published for the object.
    Then an IObjectModifiedEvent is published for the container.

    When an object is removed from a container, if the object has an
    IDeleteNotifiable adapter, that adapter's 'manage_beforeDelete' method
    is called. Then, an IObjectRemovedEvent is published for the object.
    Then an IObjectModifiedEvent is published for the container.

    When an object gets moved, it is a bit like being deleted and then added.
    For many kinds of things you'd want to do in manage_afterAdd and
    manage_beforeDelete, it is entirely appropriate to do these things
    when an object is moved. However, in other cases you want special
    behaviour on a move. So, IMoveNotifiable extends both IDeleteNotifiable
    and IAddNotifiable, adds no further methods, but extends the method
    signatures. This avoids the problem of an object that needs to be
    notified of moves and of deletes, and do something different in each
    case.

    See zope.app.interrfaces.container.IMoveNotifiable and
    zope.app.interrfaces.container.ICopyNotifiable.

    The IZopeContainerAdapter is responsible for calling the hooks and
    sending the events when you add or remove things from a container.

  Renaming

    Renaming an object is performed by moving it.

    The ZopeContainerAdapter should be extended with a 'rename' method
    for renaming an object in a container. This will be used by the
    simple UI gesture for renaming something.

    The rename method looks like this::

      def rename(currentKey, newKey):
          '''Put the object found at 'currentKey' under 'newKey' instead.

          The container can choose different or modified 'newKey'. The
          'newKey' that was used is returned.

          If the object at 'currentKey' is IMoveNotifiable, its
          manage_beforeDelete method is called, with a movingTo
          argument of the container's path plus the 'newKey'.
          Otherwise, if the object at 'currentKey' is IDeleteNotifiable,
          its manage_beforeDelete method is called.

          Then, the object is removed from the container using the
          container's __del__ method.

          Then, If the object is IMoveNotifiable, its manage_afterAdd
          method is called, with a movedFrom argument of the container's
          path plus the 'currentKey'.
          Otherwise, if the object is IAddNotifiable, its manage_afterAdd
          method is called.

          Then, an IObjectMovedEvent is published.
          '''

   Note that zope.app.interfaces.event.IObjectMovedEvent extends
   both zope.app.interfaces.event.IObjectRemovedEvent and
   zope.app.interfaces.event.IObjectAddedEvent.

   Similarly zope.app.interfaces.event.IObjectCopiedEvent extends
   should be made to IObjectAddedEvent.

 Moving and copying

   IObjectMover is what you adapt an object to when you want to move
   it. The adapter is responsible for calling the manage_beforeDelete and 
   manage_afterAdd methods on an I(Add|Delete|Move)Notifiable adapter of
   the object, as described above.
   The IObjectMover adapter is also responsible for publishing an
   IObjectMoved event in the context of the original container.

   The 'moveTo()' method will get hold of an IMoveSource for
   the object's container, and an IPasteTarget for the container the object
   is being moved to.

   Likewise, IObjectCopier is what you adapt an object to when you want to
   copy it. The IObjectCopier adapter is responsible for calling a 
   manage_afterAdd hook on an I(Add|Copy)Notifiable adapter of the object.

  The zope.app.interrfaces.container.IPasteTarget,
  zope.app.interrfaces.container.IMoveSource, and
  zope.app.interrfaces.container.ICopySource interfaces are designed
  to be independent of IContainer.  Adapters will be available for
  IContainer, though. The idea is that it should be easy for
  non-container classes to implement copy and paste, without having to
  be containers.

  A zope.app.interrfaces.container.IPasteTarget adapter must be
  available for the object you want to copy or move something into.

  A zope.app.interrfaces.container.IMoveSource adapter must be
  available for an object you want to move something from.

  Similarly, a zope.app.interrfaces.container.ICopySource adapter must
  be available for an object you want to copy something from.

Stepped out examples

  These examples are simplified, and assume things, such as that an 
  IPasteTarget adapter is unconditionally available, and copying across
  databases is not supported.

  Copying the object at '/foo/bar/baz' to '/fish/tree/zab'

    Basic application code::

      obj = traverse(context, '/foo/bar/baz')
      target = traverse(context, '/fish/tree')
      copier = getAdapter(obj, IObjectCopier)
      if copier.copyableTo(target, 'zab'):
          copier.copy(target, 'zab')

    Inside the 'copier.copyableTo()' method::

      def copyableTo(self, target, name=None):
          obj = self.context
          if name is None:
              name = objectName(obj)
          pastetarget = getAdapter(target, IPasteTarget)
          return pastetarget.acceptsObject(name, obj)

    Inside the 'copier.copy()' method::

      def copy(self, target, name=None):
          obj = self.context
          if name is None:
              name = objectName(obj)
          copysource = getAdapter(getParent(obj), ICopySource)
          obj = copysource.copyObject(name, target)
          pastetarget = getAdapter(target, IPasteTarget)
          new_obj = self._pickle_then_unpickle(obj)
          # publish an ObjectCreatedEvent (perhaps...?)
          new_name = pastetarget.pasteObject(name, new_obj)
          # call manage_afterAdd hook
          # publish ObjectCopiedEvent
          return new_name

      def _pickle_then_unpickle(self, obj):
          # Remove proxies from obj, pickle and then unpickle it. 
          # Return the result. Or, something like that
          ....


$Id: copypastemove.py,v 1.5 2003/06/12 11:04:56 jim Exp $
"""

from zope.interface import Interface

class IObjectMover(Interface):
    '''Use getAdapter(obj, IObjectMover) to move an object somewhere.'''

    def moveTo(target, new_name=None):
        '''Move this object to the target given.

        Returns the new name within the target
        Typically, the target is adapted to IPasteTarget.'''

    def moveable():
        '''Returns True if the object is moveable, otherwise False.'''

    def moveableTo(target, name=None):
        '''Say whether the object can be moved to the given target.

        Returns True if it can be moved there. Otherwise, returns
        false.
        '''

class IObjectCopier(Interface):

    def copyTo(target, new_name=None):
        """Copy this object to the target given.

        Returns the new name within the target, or None
        if the target doesn't do names.
        Typically, the target is adapted to IPasteTarget.
        After the copy is added to the target container, publish
        an IObjectCopied event in the context of the target container.
        If a new object is created as part of the copying process, then
        an IObjectCreated event should be published.
        """

    def copyable():
        '''Returns True if the object is copyable, otherwise False.'''

    def copyableTo(target, name=None):
        '''Say whether the object can be copied to the given target.

        Returns True if it can be copied there. Otherwise, returns
        False.
        '''

class INoChildrenObjectCopier(IObjectCopier):
    """Interface for adapters that can copy an containerish object
    without its children"""

    def copyTo(target, new_name=None):
        """Copy this object without chidren to the target given.

        Returns the new name within the target, or None
        if the target doesn't do names.
        Typically, the target is adapted to IPasteTarget.
        After the copy is added to the target container, publish
        an IObjectCopied event in the context of the target container.
        If a new object is created as part of the copying process, then
        an IObjectCreated event should be published.
        """

class IPrincipalClipboard(Interface):
    '''Interface for adapters that store/retrieve clipboard information
    for a principal.

    Clipboard information consists on tuples of {'action':action, 'target':target}.
    '''

    def clearContents():
        '''Clear the contents of the clipboard'''

    def addItems(action, targets):
        '''Add new items to the clipboard'''

    def setContents(clipboard):
        '''Replace the contents of the clipboard by the given value'''

    def getContents():
        '''Return the contents of the clipboard'''
