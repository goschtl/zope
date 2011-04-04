##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
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


from zope.component import getUtility
from zope.formlib.form import action
from zope.formlib.form import Fields
from zope.formlib.form import Form
from zope.interface import Interface
from zope.publisher.browser import BrowserView
from zope.schema import TextLine

from zc.openid.interfaces import IOpenIDConsumer


class IChooseIdentitySchema(Interface):
    url = TextLine(title=u'OpenID URL')

class ChooseIdentityForm(Form):
    label = u'OpenID Login'
    form_fields = Fields(IChooseIdentitySchema)

    @action(u"Login")
    def login(self, action, data):
        auth = getUtility(IOpenIDConsumer, context=self)
        auth.login(self.request, data['url'])


class OpenIDView(BrowserView):

    def choose_identity(self):
        return ChooseIdentityForm(self.context, self.request)()

    def login(self):
        auth = getUtility(IOpenIDConsumer, context=self)
        auth.login(self.request)

    def complete(self):
        auth = getUtility(IOpenIDConsumer, context=self)
        auth.complete(self.request)

