##############################################################################
#
# Copyright (c) 2010 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Upgrade steps to CMFDefault 2.3.
"""

import logging

from zope.component import getMultiAdapter

from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent
from OFS.userfolder import UserFolder
from Products.CMFCore.utils import getToolByName
from Products.GenericSetup.context import SetupEnviron
from Products.GenericSetup.interfaces import IBody

_MARKER = object()

def check_cookie_crumbler(tool):
    """2.2.x to 2.3.0 upgrade step checker
    """
    cctool = getToolByName(tool, 'cookie_authentication', None)
    if cctool is None:
        return False
    cctool = aq_base(cctool)
    for name in ('auto_login_page', 'unauth_page', 'logout_page'):
        if getattr(cctool, name, _MARKER) is not _MARKER:
            return True
    return False

def upgrade_cookie_crumbler(tool):
    """2.2.x to 2.3.0 upgrade step handler
    """
    logger = logging.getLogger('GenericSetup.upgrade')
    cctool = getToolByName(tool, 'cookie_authentication', None)
    if cctool is None:
        return
    cctool = aq_base(cctool)
    for name in ('auto_login_page', 'unauth_page', 'logout_page'):
        if getattr(cctool, name, _MARKER) is not _MARKER:
            delattr(cctool, name)
            logger.info("Cookie crumbler property '%s' removed." % name)

def check_setup_tool(tool):
    """2.2.x to 2.3.0 upgrade step checker
    """
    registry = tool.getToolsetRegistry()
    try:
        info = registry.getRequiredToolInfo('acl_users')
        if info['class'] == 'AccessControl.User.UserFolder':
            return True
    except KeyError:
        return False
    return False

def upgrade_setup_tool(tool):
    """2.2.x to 2.3.0 upgrade step handler
    """
    logger = logging.getLogger('GenericSetup.upgrade')
    registry = tool.getToolsetRegistry()
    try:
        info = registry.getRequiredToolInfo('acl_users')
        if info['class'] == 'AccessControl.User.UserFolder':
            info['class'] = 'OFS.userfolder.UserFolder'
            tool._p_changed = True
            logger.info("Updated class registered for 'acl_users'.")
    except KeyError:
        return

def check_acl_users(tool):
    """2.2.x to 2.3.0 upgrade step checker
    """
    from AccessControl.User import UserFolder as OldUserFolder

    portal = aq_parent(aq_inner(tool))
    users = aq_base(portal.acl_users)
    if not getattr(users, '_ofs_migrated', False):
        if users.__class__ is OldUserFolder:
            return True
    return False

def upgrade_acl_users(tool):
    """2.2.x to 2.3.0 upgrade step handler
    """
    from AccessControl.User import UserFolder as OldUserFolder

    logger = logging.getLogger('GenericSetup.upgrade')
    portal = aq_parent(aq_inner(tool))
    users = aq_base(portal.acl_users)
    if not getattr(users, '_ofs_migrated', False):
        if users.__class__ is OldUserFolder:
            users.__class__ = UserFolder
            users._ofs_migrated = True
            users._p_changed = True
            logger.info("Updated UserFolder class.")

def check_actions_tool(tool):
    """2.2.x to 2.3.0 upgrade step checker
    """
    atool = getToolByName(tool, 'portal_actions')
    try:
        atool.user.change_password
    except AttributeError:
        return True
    try:
        atool.user.syndication
    except AttributeError:
        return True
    return False

def upgrade_actions_tool(tool):
    """2.2.x to 2.3.0 upgrade step handler
    """
    logger = logging.getLogger('GenericSetup.upgrade')
    atool = getToolByName(tool, 'portal_actions')
    environ = SetupEnviron()
    environ._should_purge = False
    getMultiAdapter((atool, environ), IBody).body = _ACTIONS_PASSWORD_XML
    logger.info("'change_password' action added.")
    getMultiAdapter((atool, environ), IBody).body = _ACTIONS_SYNDICATION_XML
    logger.info("'portal syndication settings' action added.")

_ACTIONS_PASSWORD_XML = """\
<?xml version="1.0"?>
<object name="portal_actions" meta_type="CMF Actions Tool"
   xmlns:i18n="http://xml.zope.org/namespaces/i18n">
 <object name="user" meta_type="CMF Action Category">
  <object insert-after="join" name="change_password" meta_type="CMF Action"
     i18n:domain="cmf_default">
   <property name="title" i18n:translate="">Change password</property>
   <property name="description"
      i18n:translate="">Change your password</property>
   <property name="url_expr">string:${portal_url}/password_form</property>
   <property name="link_target"></property>
   <property
      name="icon_expr">string:${portal_url}/preferences_icon.png</property>
   <property name="available_expr">member</property>
   <property name="permissions">
    <element value="Set own password"/>
   </property>
   <property name="visible">True</property>
  </object>
 </object>
</object>
"""

_ACTIONS_SYNDICATION_XML = """\
<object name="portal_actions" meta_type="CMF Actions Tool"
   xmlns:i18n="http://xml.zope.org/namespaces/i18n">
 <object name="global" meta_type="CMF Action Category">
  <object name="syndication" meta_type="CMF Action" i18n:domain="cmf_default">
   <property name="title" i18n:translate="">Site Syndication</property>
   <property name="description"
      i18n:translate="">Enable or  disable syndication</property>
   <property
      name="url_expr">string:${portal_url}/@@syndication.html</property>
   <property name="link_target"></property>
   <property name="icon_expr">string:${portal_url}/tool_icon.png</property>
   <property name="available_expr"></property>
   <property name="permissions">
    <element value="Manage portal"/>
   </property>
   <property name="visible">True</property>
  </object>
 </object>
</object>
"""
