##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
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
"""interfaces for listcontainer and events

A smaller, parallel pattern based on zope.app.container

$Id: interfaces.py 700 2005-02-23 16:53:35Z gary $
"""
from zope import interface
from zope.interface.common import sequence
from zope.component.interfaces import IObjectEvent

class IContainedObjectEvent(IObjectEvent):
    """An object's super or predecessor has changed (not successor).

    An abstract interface; use a subclass."""

    oldSuper = interface.Attribute("The old listcontainer for the object.")
    oldPrevious = interface.Attribute("The old previous sibling for the object.")
    oldNext = interface.Attribute("The old next sibling for the object.")
    newSuper = interface.Attribute("The new listcontainer for the object.")
    newPrevious = interface.Attribute("The new previous sibling for the object.")
    newNext = interface.Attribute("The new next sibling for the object.")

class IObjectMovedEvent(IContainedObjectEvent):
    """An object's super has changed."""

class IObjectReorderedEvent(IContainedObjectEvent):
    """An object's predecessor has changed, but the super is the same"""

class IObjectAddedEvent(IObjectMovedEvent):
    "An object has been added"

class IObjectRemovedEvent(IObjectMovedEvent):
    "An object has been removed"

class IObjectReplacedEvent(IObjectRemovedEvent):
    "An object has been replaced."

    replacement = interface.Attribute(
        "The value with which the object has been replaced.")
    replacementOldSuper = interface.Attribute(
        "The old listcontainer for the replacement.")
    replacementOldPrevious = interface.Attribute(
        "The old previous sibling for the replacement.")
    replacementOldNext = interface.Attribute(
        "The old next sibling for the replacement.")
    replacementNewSuper = interface.Attribute(
        "The new listcontainer for the replacement.")
    replacementNewPrevious = interface.Attribute(
        "The new previous sibling for the replacement.")
    replacementNewNext = interface.Attribute(
        "The new next sibling for the replacement.")

class IContained(interface.Interface):
    super = interface.Attribute("""\
        the listcontainer of the object; None if not contained""")

    next = interface.Attribute("""\
        the next contained object in the listcontainer, or None""")

    previous = interface.Attribute("""\
        the previous contained object in the listcontainer, or None""")

class IListContainer(sequence.IExtendedReadSequence, 
                     sequence.IUniqueMemberWriteSequence):
    """pseudo-list interface: events, unique containment, linked list.

    Contained items must support IContained.

    Does not support inplace multiplication or setslice by step.
    """

    def silentpop(i=-1):
        """pops item off list without firing events.

        Maintains linked list attributes of siblings and sets popped items's
        IContained attributes to None.
        """

    def moveinsert(i, *items):
        """inserts items; deletes from previous listcontainer, if any.

        Maintains IContained links.  Fires events, as appropriate.
        """

    def moveappend(item):
        """appends item; deletes from previous listcontainer, if any.

        Maintains IContained links.  Fires events as appropriate.
        """

    def moveextend(iterable):
        """extends list with items in iterable; deleted from previous
        listcontainer, if any.

        Maintains IContained links.  Fires events as approproate.
        """

    def movereplace(i, item):
        """replaces member at index i with item.  item deleted from previous
        listcontainer, if any.

        Maintains IContained links.  Fires events as appropriate.
        """
