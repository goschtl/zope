##############################################################################
#
# Copyright (c) 2006-2007 Zope Foundation and Contributors.
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
"""Grok components"""

from zope.security.permission import Permission

def api(name):
    from zope.dottedname.resolve import resolve
    from zope.interface import Interface

    try:
        return True, resolve(name)
    except ImportError:
        return False, Interface


class Permission(Permission):
    pass

Public = 'zope.Public'


HAVE_ROLE, securitypolicy_Role = api('zope.securitypolicy.role.Role')

if HAVE_ROLE:
    class Role(securitypolicy_Role):
        """Base class for roles in Grok applications.

        A role is a description of a class of users that gives them a
        machine-readable name, a human-readable title, and a set of
        permissions which users belong to that role should possess::

            class Editor(grok.Role):
                grok.name('news.Editor')
                grok.title('Editor')
                grok.permissions('news.EditArticle', 'news.PublishArticle')

        """
