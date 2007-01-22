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
"""Adding that redirects to plugins.html.

$Id$
"""

from zope.formlib import form

from z3c.i18n import MessageFactory as _
from z3c.authentication.simple import interfaces


class EditMember(form.EditForm):
    """Group edit form."""

    label = _('Edit Member.')

    form_fields = form.Fields(interfaces.IMember).select('login', 'password', 
        'title', 'description', 'passwordManagerName')


class EditGroup(form.EditForm):
    """Group edit form."""

    label = _('Edit Group.')

    form_fields = form.Fields(interfaces.IGroup).select('title', 
        'description', 'principals')
