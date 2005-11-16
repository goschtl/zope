##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors. All Rights
# Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this
# distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Export / import adapters for stock PAS plugins.

$Id$
"""
from xml.dom.minidom import parseString

from Acquisition import Implicit
from zope.interface import implements

from Products.GenericSetup.interfaces import IFilesystemExporter
from Products.GenericSetup.interfaces import IFilesystemImporter

try:
    from Products.GenericSetup.utils import PageTemplateResource
except ImportError: # BBB
    from Products.PageTemplates.PageTemplateFile \
        import PageTemplateFile as PageTemplateResource

class SimpleXMLExportImport(Implicit):
    """ Base for plugins whose configuration can be dumped to an XML file.

    o Derived classes must define:

      '_FILENAME' -- a class variable naming the export template

      '_getExportInfo' --  a method returning a mapping which will be passed
       to the template as 'info'.

      '_ROOT_TAGNAME' -- the name of the root tag in the XML (for sanity check)

      '_purgeContext' -- a method which clears our context.

      '_updateFromDOM' -- a method taking the root node of the DOM.
    """
    implements(IFilesystemExporter, IFilesystemImporter)

    def __init__(self, context):
        self.context = context

    def export(self, export_context, subdir, root=False):
        """ See IFilesystemExporter.
        """
        template = PageTemplateResource('xml/%s' % self._FILENAME,
                                        globals()).__of__(self.context)
        info = self._getExportInfo()
        export_context.writeDataFile('%s.xml' % self.context.getId(),
                                     template(info=info),
                                     'text/xml',
                                     subdir,
                                    )

    def listExportableItems(self):
        """ See IFilesystemExporter.
        """
        return ()

    def import_(self, import_context, subdir, root=False):
        """ See IFilesystemImporter
        """
        if import_context.shouldPurge():
            self._purgeContext()

        data = import_context.readDataFile('%s.xml' % self.context.getId(),
                                           subdir)

        if data is not None:

            dom = parseString(data)
            root = dom.firstChild
            assert root.tagName == self._ROOT_TAGNAME

            title = root.attributes.get('title')

            if title is not None:
                title = title.value

            self.context.title = title

            self._updateFromDOM(root)

class ZODBUserManagerExportImport(SimpleXMLExportImport):
    """ Adapter for dumping / loading ZODBUSerManager to an XML file.
    """
    implements(IFilesystemExporter, IFilesystemImporter)

    _FILENAME = 'zodbusers.xml'
    _ROOT_TAGNAME = 'zodb-users'

    def _purgeContext(self):
        self.context.__init__(self.context.id, self.context.title)

    def _updateFromDOM(self, root):
        for user in root.getElementsByTagName('user'):
            user_id = user.attributes['user_id'].value
            login_name = user.attributes['login_name'].value
            password_hash = user.attributes['password_hash'].value

            self.context.addUser(user_id, login_name, 'x')
            self.context._user_passwords[user_id] = password_hash

    def _getExportInfo(self):
        user_info = []

        for uinfo in self.context.listUserInfo():
            user_id = uinfo['user_id']

            info = {'user_id': user_id,
                    'login_name': uinfo['login_name'],
                    'password_hash': self.context._user_passwords[user_id],
                   }

            user_info.append(info)

        return {'title': self.context.title,
                'users': user_info,
               }


class ZODBGroupManagerExportImport(SimpleXMLExportImport):
    """ Adapter for dumping / loading ZODBGroupManager to an XML file.
    """
    _FILENAME = 'zodbgroups.xml'
    _ROOT_TAGNAME = 'zodb-groups'

    def _purgeContext(self):
        self.context.__init__(self.context.id, self.context.title)

    def _updateFromDOM(self, root):

        for group in root.getElementsByTagName('group'):
            group_id = group.attributes['group_id'].value
            title = group.attributes['title'].value
            description = group.attributes['description'].value

            self.context.addGroup(group_id, title, description)

            for principal in group.getElementsByTagName('principal'):
                principal_id = principal.attributes['principal_id'].value
                self.context.addPrincipalToGroup(principal_id, group_id)

    def _getExportInfo(self):
        group_info = []
        for ginfo in self.context.listGroupInfo():
            group_id = ginfo['id']
            info = {'group_id': group_id,
                    'title': ginfo['title'],
                    'description': ginfo['description'],
                   }
            info['principals'] = self._listGroupPrincipals(group_id) 
            group_info.append(info)
        return {'title': self.context.title,
                'groups': group_info,
               }

    def _listGroupPrincipals(self, group_id):
        """ List the principal IDs of the group's members.
        """
        result = []
        for k, v in self.context._principal_groups.items():
            if group_id in v:
                result.append(k)
        return tuple(result)



class ZODBRoleManagerExportImport(SimpleXMLExportImport):
    """ Adapter for dumping / loading ZODBGroupManager to an XML file.
    """
    _FILENAME = 'zodbroles.xml'
    _ROOT_TAGNAME = 'zodb-roles'

    def _purgeContext(self):
        self.context.__init__(self.context.id, self.context.title)

    def _updateFromDOM(self, root):
        for role in root.getElementsByTagName('role'):
            role_id = role.attributes['role_id'].value
            title = role.attributes['title'].value
            description = role.attributes['description'].value

            self.context.addRole(role_id, title, description)

            for principal in role.getElementsByTagName('principal'):
                principal_id = principal.attributes['principal_id'].value
                self.context.assignRoleToPrincipal(role_id, principal_id)

    def _getExportInfo(self):
        role_info = []

        for rinfo in self.context.listRoleInfo():
            role_id = rinfo['id']
            info = {'role_id': role_id,
                    'title': rinfo['title'],
                    'description': rinfo['description'],
                   }
            info['principals'] = self._listRolePrincipals(role_id) 
            role_info.append(info)

        return {'title': self.context.title,
                'roles': role_info,
               }

    def _listRolePrincipals(self, role_id):
        """ List the principal IDs of the group's members.
        """
        result = []
        for k, v in self.context._principal_roles.items():
            if role_id in v:
                result.append(k)
        return tuple(result)

