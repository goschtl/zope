##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""Add forms

$Id$
"""

import zope.interface
import zope.schema
from zope.formlib import form

from z3c.i18n import MessageFactory as _
from z3c.authentication.simple import interfaces
from z3c.authentication.simple import group
from z3c.authentication.simple import member


class IContentName(zope.interface.Interface):
    """Object name."""

    __name__ = zope.schema.TextLine( 
        title=u'Object Name',
        description=u'Object Name',
        required=True)


class MemberContainerAddForm(form.AddForm):
    """MemberContainer add form."""

    label = _('Add Member Container.')

    form_fields = form.Fields(IContentName)

    def create(self, data):
        obj = member.MemberContainer()
        self.context.contentName = data.get('__name__', u'')
        return obj


class MemberAddForm(form.AddForm):
    """Member add form."""

    label = _('Add Member.')

    form_fields = form.Fields(interfaces.IMember).select('login', 'password', 
        'title', 'description', 'passwordManagerName')
    form_fields += form.Fields(IContentName)

    def create(self, data):
        login = data.get('login', u'')
        password = data.get('password', u'')
        title = data.get('title', u'')
        description = data.get('description', u'')
        passwordManagerName = data.get('passwordManagerName', u'')
        obj = member.Member(login, password, title, description, 
            passwordManagerName)
        name = data.get('__name__', u'')
        self.context.contentName = name
        return obj



class GroupContainerAddForm(form.AddForm):
    """GroupContainer add form."""

    label = _('Add Group Container.')

    form_fields = form.Fields(interfaces.IGroupContainer).select(
        'prefix')
    form_fields += form.Fields(IContentName)

    def create(self, data):
        obj = group.GroupContainer()
        obj.prefix = data.get('prefix', u'')
        self.context.contentName = data.get('__name__', u'')
        return obj


class GroupAddForm(form.AddForm):
    """Group add form."""

    label = _('Add Group.')

    form_fields = form.Fields(interfaces.IGroup).select('title', 'description')
    form_fields += form.Fields(IContentName)

    def create(self, data):
        title = data.get('title', u'')
        description = data.get('description', u'')
        obj = group.Group(title, description)
        name = data.get('__name__', u'')
        prefix = self.context.context.prefix
        if not name.startswith(prefix):
            name = prefix + name
        self.context.contentName = name
        return obj