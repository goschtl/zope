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
"""Provide persistent wrappers for objects that cannot derive from
persistence for some reason."""

from persistence import Persistent

class Struct(Persistent):
  """Wraps a non-persistent object, assuming that *all* changes are
  made through external attribute assignments.
  """

  def __init__(self, o):
    self.__proxied__ = o

  def __getattr__(self, name):
    if name.startswith('_p_') or name in ['__proxied__']:
      return object.__getattribute__(self, name)
    return getattr(self.__proxied__, name)

  def __setattr__(self, name, v):
    if name.startswith('_p_') or name in ['__proxied__']:
      return Persistent.__setattr__(self, name, v)
    setattr(self.__proxied__, name, v)
    self._p_changed = 1

  def __delattr__(self, name):
    if name.startswith('_p_') or name in ['__proxied__']:
      return Persistent.__delattr__(self, name)
    delattr(self.__proxied__, name, v)
    self._p_changed = 1
