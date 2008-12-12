##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""I18n Messages

$Id$
"""
__docformat__ = "reStructuredText"

from weakref import WeakKeyDictionary
registry = WeakKeyDictionary()

class Message(unicode):
    """Message (Python implementation)

    This is a string used as a translation message. It has a
    ``domain`` attribute that is its translation domain, and a
    ``default`` attribute that is its default text to display when
    there is no translation. ``domain`` may be ``None`` meaning there
    is no translation domain; ``default`` may also be ``None``, in
    which case the message id itself implicitly serves as the default
    text.

    >>> from zope.i18nmessageid.message import Message
    >>> robot = Message(u"robot-message", 'futurama', u"${name} is a robot.")

    >>> robot
    u'robot-message'
    >>> isinstance(robot, unicode)
    True

    >>> robot.default
    u'${name} is a robot.'
    >>> robot.mapping

    >>> robot.domain = "planetexpress"
    Traceback (most recent call last):
    ...
    AttributeError: can't set attribute

    >>> robot.default = u"${name} is not a robot."
    Traceback (most recent call last):
    ...
    AttributeError: can't set attribute

    >>> robot.mapping = {u'name': u'Bender'}
    Traceback (most recent call last):
    ...
    AttributeError: can't set attribute

    >>> new_robot = Message(robot, mapping={u'name': u'Bender'})
    
    >>> new_robot
    u'robot-message'
    
    >>> new_robot.domain
    'futurama'
    
    >>> new_robot.default
    u'${name} is a robot.'
    
    >>> new_robot.mapping
    {u'name': u'Bender'}

    Verify that messages reduces to their arguments.

    >>> callable, args = new_robot.__reduce__()
    >>> callable is Message
    True
    
    >>> args
    (u'robot-message', 'futurama', u'${name} is a robot.', {u'name': u'Bender'})

    >>> fembot = Message(u'fembot')
    
    >>> callable, args = fembot.__reduce__()
    >>> callable is Message
    True
    
    >>> args
    (u'fembot', None, None, None)
    
    Verify pickling. First, pickle the message.
    
    >>> from pickle import dumps, loads
    >>> pystate = dumps(new_robot)
    
    Verify that we have an empty registry when there are no hard
    references to the messages.
    
    >>> from zope.i18nmessageid.message import registry
    >>> del robot, fembot, new_robot
    >>> len(registry)
    0
    
    Load the pickle and verify registry.
    
    >>> pickle_bot = loads(pystate)
    >>> len(registry)
    1

    We expect the message properties to be available.
    
    >>> pickle_bot, pickle_bot.domain, pickle_bot.default, pickle_bot.mapping
    (u'robot-message', 'futurama', u'${name} is a robot.', {u'name': u'Bender'})
    
    """

    def __new__(cls, ustr, domain=None, default=None, mapping=None):
        self = unicode.__new__(cls, ustr)
        if isinstance(ustr, self.__class__):
            domain = ustr.domain and ustr.domain[:] or domain
            default = ustr.default and ustr.default[:] or default
            mapping = ustr.mapping and ustr.mapping.copy() or mapping
            ustr = unicode(ustr)

        # make sure a non-trivial default value is a unicode string
        if default is not None:
            default = unicode(default)

        registry[self] = (domain, default, mapping)
        return self

    def __reduce__(self):
        return type(self), self.__getstate__()

    def __getstate__(self):
        return unicode(self), self.domain, self.default, self.mapping

    @property
    def domain(self):
        return registry[self][0]

    @property
    def default(self):
        return registry[self][1]

    @property
    def mapping(self):
        return registry[self][2]

class MessageFactory(object):
    """Factory for creating i18n messages."""

    def __init__(self, domain):
        self._domain = domain

    def __call__(self, ustr, default=None, mapping=None):
        return Message(ustr, self._domain, default, mapping)
