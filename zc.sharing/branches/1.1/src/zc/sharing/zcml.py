##############################################################################
#
# Copyright (c) 2003 Zope Corporation. All Rights Reserved.
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
"""ZCML directives for defining privileges.

$Id$
"""

from types import ClassType

from zope import component, interface, schema
import zope.configuration.fields
import zope.security.zcml

from zc.sharing import policy, sharing, interfaces

class IdefinePrivilege(interface.Interface):

    bit = schema.Int(
        title=u"Privilege bit",
        description=(u"The privilege ID should be a small positive "
                     u"integer, as it is actually a bit "
                     u"identifier. User privileges are stored as bits "
                     u"in a sharing value."),
        )

    title = zope.configuration.fields.MessageID(
        title=u"Title",
        description=u"A user-friendly name for the privilege",
        )

    description = zope.configuration.fields.MessageID(
        title=u"Description",
        description=(u"A description of the privilege, including "
                     u"the capabilities the privilege provides"),
        required=False,
        )

def definePrivilege(_context, bit, title, description=''):
    _context.action(
        discriminator=('zc.intranet:privilege', bit),
        callable=sharing.definePrivilege,
        args=(bit, title, description, _context.info),
        )

class IpermissionPrivilege(interface.Interface):

    permission = zope.security.zcml.Permission(
        title=u"Permission",
        description=u"Permission for which a privilege is being defined",
        )

    privilege = schema.Int(
        title=u"Privilege",
        description=u"The privilege ID that provides the permission",
        )
        
def checkPrivilege(privilege):
    if sharing.getPrivilege(privilege, -1) < 0:
        raise ValueError("Undefined privilege", privilege)

def permissionPrivilege(_context, permission, privilege):
    _context.action(
        discriminator=None,
        callable=checkPrivilege,
        args=(privilege, )
        )
    _context.action(
        discriminator=('zc:permissionPrivilege', permission),
        callable=policy.permissionPrivilege,
        args=(permission, privilege),
        )

class Iprivileges(interface.Interface):

    for_ = zope.configuration.fields.GlobalObject(
        title=u"Type the privileges are used for"
        )

    titles = zope.configuration.fields.Tokens(
        title=u"Privileges",
        description=u"List of privilege titles",
        value_type=schema.TextLine(),
        )

for_types = type(None), type, type(interface.Interface), ClassType
def privileges(_context, for_, titles):

    if not isinstance(for_, for_types):
        raise TypeError("Invalid type for for", type(for_))
    _context.action(
        discriminator=('zc:privileges', for_),
        callable=policy.sharingPrivileges,
        args=(for_, titles),
        )

def subobjectPrivileges(_context, for_, titles):

    if not isinstance(for_, for_types):
        raise TypeError("Invalid type for for", type(for_))
    _context.action(
        discriminator=('zc:subobjectPrivileges', for_),
        callable=policy.subobjectSharingPrivileges,
        args=(for_, titles),
        )

class IsystemAdministrators(interface.Interface):

    principals = zope.configuration.fields.Tokens(
        title=u"Principals",
        description=u"System administrator principal ids",
        value_type=schema.TextLine(),
        )

def setSystemAdministrators(principals):
    policy.systemAdministrators = principals
    
def systemAdministrators(_context, principals):
    _context.action(
        discriminator='zc:sysAdmins',
        callable=setSystemAdministrators,
        args=(tuple(principals), )
        )
