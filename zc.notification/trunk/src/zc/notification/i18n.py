##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Visible Source
# License, Version 1.0 (ZVSL).  A copy of the ZVSL should accompany this
# distribution.
#
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""I18N support for zc.notification.

This defines a `MessageFactory` for the I18N domain for the
zc.notification package.  This is normally used with the import::

  from zc.notification.i18n import MessageFactory as _

The factory is then used normally.  Two examples::

  text = _('some internationalized text')
  text = _('helpful-descriptive-message-id', 'default text')
"""
__docformat__ = "reStructuredText"


from zope import i18nmessageid

MessageFactory = _ = i18nmessageid.MessageFactory("zc.notification")
