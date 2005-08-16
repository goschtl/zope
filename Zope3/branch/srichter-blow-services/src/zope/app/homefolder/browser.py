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
"""Home Folder related views.

$Id$
"""
__docformat__ = "reStructuredText"
import zope.schema
from zope.schema.vocabulary import SimpleVocabulary
from zope.security.proxy import removeSecurityProxy

from zope.app import zapi
from zope.app.form.browser import TextWidget, MultiSelectWidget
from zope.app.form.utility import setUpWidget
from zope.app.form.interfaces import IInputWidget
from zope.app.security.vocabulary import PrincipalSource 

class PathWidget(TextWidget):

    def _toFieldValue(self, input):
        path = super(PathWidget, self)._toFieldValue(input)
        root = zapi.getRoot(self.context.context)
        return removeSecurityProxy(zapi.traverse(root, path))
    
    def _toFormValue(self, value):
        if value is None:
            return ''
        return zapi.getPath(value)


class AssignHomeFolder(object):

    def setupWidgets(self):
        self.principal_field = zope.schema.Choice(
            __name__ = 'principal',
            title=u'Principal Id',
            source=PrincipalSource(),
            required=False)
    
        self.folderName_field = zope.schema.TextLine(
            __name__ = 'folderName',
            title=u'Folder Name',
            required=False)

        self.selectedPrincipals_field = zope.schema.List(
            __name__ = 'selectedPrincipals',
            title=u'Existing Assignments',
            value_type=zope.schema.Choice(
                vocabulary=SimpleVocabulary.fromItems(
                    [('%s (%s)' %(key, value), key)
                     for key, value in self.context.assignments.items()]
                    )),
            required=False)

        setUpWidget(self, 'principal', self.principal_field, IInputWidget)
        setUpWidget(self, 'folderName', self.folderName_field, IInputWidget)
        self.selectedPrincipals_widget = MultiSelectWidget(
            self.selectedPrincipals_field.bind(self),
            self.selectedPrincipals_field.value_type.vocabulary,
            self.request)
        self.selectedPrincipals_widget.setRenderedValue([])

    def update(self):
        self.setupWidgets()

        if 'SUBMIT_ASSIGN' in self.request:
            if not self.principal_widget.hasInput():
                return u''

            principal = self.principal_widget.getInputValue()
            name = self.folderName_widget.getInputValue()
        
            self.context.assignHomeFolder(principal, name)
            self.setupWidgets()
            return u'Home Folder assignment was successful.'

        if 'SUBMIT_UNASSIGN' in self.request:
            if not self.selectedPrincipals_widget.hasInput():
                return u''

            for id in self.selectedPrincipals_widget.getInputValue():
                self.context.unassignHomeFolder(id)

            self.setupWidgets()
            return u'Principals were successfully unassigned.'

        return u''
