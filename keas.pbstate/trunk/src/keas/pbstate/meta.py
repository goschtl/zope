##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
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
"""Provides the ProtobufState metaclass."""

from google.protobuf.descriptor import FieldDescriptor

from keas.pbstate.state import StateTuple


def _protobuf_property(name):
    """A property that delegates to a protobuf message"""
    def get(self):
        return getattr(self.protobuf, name)
    def set(self, value):
        setattr(self.protobuf, name, value)
    def delete(self):
        delattr(self.protobuf, name)
    return property(get, set, delete)


def _protobuf_mixin_property(container_getter, name):
    """A property that delegates to a protobuf sub-message"""
    def get_(self):
        return getattr(container_getter(self), name)
    def set_(self, value):
        setattr(container_getter(self), name, value)
    def del_(self):
        delattr(container_getter(self), name)
    return property(get_, set_, del_)


def _add_mixin(created_class, mixin_name):
    """Add the properties from a protobuf sub-message to a class"""
    main_desc = created_class.protobuf_type.DESCRIPTOR

    # traverse to the named descriptor
    descriptor = main_desc
    parts = mixin_name.split('.')
    for name in parts:
        # find the named field
        for f in descriptor.fields:
            if f.name == name:
                descriptor = f.message_type
                break
        else:
            raise AttributeError(
                "Field %r not defined for protobuf type %r" %
                (mixin_name, main_desc))

    container_getter = eval(
        'lambda self: self.protobuf.%s' % mixin_name)

    for field in descriptor.fields:
        setattr(created_class, field.name, _protobuf_mixin_property(
            container_getter, field.name))


class MessageRefidGatherer:
    """Returns the set of used refids from a message of a certain type."""

    def __init__(self, descriptor):
        self.attrs = {}  # {attr: gather callable}
        self.has_refs = False

        # Visit certain fields in the message.
        for field in descriptor.fields:

            # set up a 'gather' callable that iterates refids,
            if field.message_type is not None:
                gather = MessageRefidGatherer(field.message_type)
                if gather.has_refs:
                    self.has_refs = True
                else:
                    # don't bother visiting this part of the message
                    continue
            elif field.name == '_p_refid':
                self.has_refs = True
                def gather(value):
                    if value:
                        yield value
            else:
                # other scalars don't matter
                continue

            if field.label == FieldDescriptor.LABEL_REPEATED:
                def gather_all(container, gather=gather):
                    for obj in container:
                        for refid in gather(obj):
                            yield refid
                gather = gather_all

            self.attrs[field.name] = gather

    def __call__(self, container):
        for name, gather in self.attrs.iteritems():
            for refid in gather(getattr(container, name)):
                yield refid


class ProtobufReferences(object):
    """A mapping-like object that gets or sets the target of references.

    A reference is a protobuf message with a _p_refid field.
    The target can be any kind of pickleable object, including derivatives
    of ZODB.Persistent.
    """
    __slots__ = ('_targets',)

    def __init__(self, targets):
        self._targets = targets  # {refid -> target}

    def __getitem__(self, message):
        """Get a reference target"""
        refid = message._p_refid
        if not refid:
            raise KeyError("No reference set")
        return self._targets[refid]

    def __setitem__(self, message, target):
        """Set the target of a reference message"""
        targets = self._targets
        refid = id(target) % 0xffffffff
        if refid not in targets or targets[refid] is not target:
            while not refid or refid in targets:
                refid = (refid + 1) % 0xffffffff
            targets[refid] = target
        message._p_refid = refid

    def __delitem__(self, message):
        """Unlink a target from a reference message"""
        # We can't actually remove the reference from the reference mapping
        # because something else might still have a reference.  __getstate__
        # will remove unused references.
        message._p_refid = 0

    def _get_targets(self, obj, used):
        """Clean out unused reference targets, then return the target dict.

        Also raises an error if there are broken references.
        obj is the object that contains this references object.  used
        is the set of _p_refids in use by the protobuf.
        """
        targets = self._targets
        current = set(targets)
        broken = used.difference(current)
        if broken:
            raise KeyError("Object contains broken references: %s" % repr(obj))
        for key in current.difference(used):
            del targets[key]
        return targets


class StateClassMethods(object):
    """Contains methods that get copied into classes using ProtobufState"""

    def __getstate__(self):
        """Encode the entire state of the object in a ProtobufState."""
        # Clean up unused references and get the targets mapping.
        used = set(self._protobuf_find_refids(self.protobuf))
        targets = self.protobuf_refs._get_targets(self, used)
        # Return the state and all reference targets.
        return StateTuple((self.protobuf.SerializeToString(), targets))

    def __setstate__(self, state):
        """Set the state of the object.

        Accepts a StateTuple or any two item sequence containing
        data (a byte string) and targets (a map of refid to object).
        """
        data, targets = state
        self.protobuf_refs = ProtobufReferences(targets)
        self.protobuf = self.protobuf_type()
        self.protobuf.MergeFromString(data)
        if hasattr(self, '_p_changed'):
            self.protobuf._SetListener(PersistentChangeListener(self))


class PersistentChangeListener(object):
  """Propagates protobuf change notifications to a Persistent container.

  Implements the interface described by
  google.protobuf.internal.message_listener.MessageListener.
  """
  __slots__ = ('obj',)

  def __init__(self, obj):
      self.obj = obj

  def TransitionToNonempty(self):
      self.obj._p_changed = True

  def ByteSizeDirty(self):
      self.obj._p_changed = True


class ProtobufState(type):
    """Metaclass for classes using a protobuf for state and serialization."""

    def __new__(metaclass, name, bases, dct):
        """Set up a new class."""

        # Arrange for class instances to always have the 'protobuf' and
        # 'protobuf_refs' instance attributes.  This is done by creating
        # or overriding the __new__() method of the new class.
        parent__new__ = dct.get('__new__')
        def __new__(subclass, *args, **kw):
            # subclass is either created_class or a subclass of created_class.
            create = parent__new__
            if create is None:
                create = super(created_class, subclass).__new__
            instance = create(subclass, *args, **kw)
            instance.protobuf_refs = ProtobufReferences({})
            instance.protobuf = subclass.protobuf_type()
            if hasattr(instance, '_p_changed'):
                instance.protobuf._SetListener(
                    PersistentChangeListener(instance))
            return instance
        dct['__new__'] = __new__

        # Limit instance attributes to avoid partial serialization.
        # Note that classes can still store temporary state by
        # declaring other attribute names in the class' __slots__
        # attribute.
        dct['__slots__'] = dct.get('__slots__', ()) + (
            'protobuf', 'protobuf_refs')

        created_class = type.__new__(metaclass, name, bases, dct)
        if not hasattr(created_class, 'protobuf_type'):
            raise TypeError("Class %s.%s needs a protobuf_type attribute"
                % (created_class.__module__, created_class.__name__))
        descriptor = created_class.protobuf_type.DESCRIPTOR

        # Copy methods into the class
        for method_name in ('__getstate__', '__setstate__'):
            setattr(created_class, method_name,
                StateClassMethods.__dict__[method_name])

        # Set up the refid gatherer
        created_class._protobuf_find_refids = MessageRefidGatherer(descriptor)

        # Create properties that delegate storage to the protobuf
        for field in descriptor.fields:
            setattr(created_class, field.name,
                _protobuf_property(field.name))

        # Create properties that delegate to mixed in attributes
        for mixin_name in dct.get('protobuf_mixins', ()):
            _add_mixin(created_class, mixin_name)

        return created_class
