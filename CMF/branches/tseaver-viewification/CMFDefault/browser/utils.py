##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Browser view utilities.

$Id$
"""

from ZTUtils import make_query

from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.utils import html_marshal
from Products.CMFDefault.utils import toUnicode
from Products.CMFDefault.utils import MessageID as _


def decode(meth):
    def decoded_meth(self, *args, **kw):
        return toUnicode(meth(self, *args, **kw), self._getDefaultCharset())
    return decoded_meth

def memoize(meth):
    def memoized_meth(self, *args):
        if not hasattr(self, '__memo__'):
            self.__memo__ = {}
        sig = (meth, args)
        if sig not in self.__memo__:
            self.__memo__[sig] = meth(self, *args)
        return self.__memo__[sig]
    return memoized_meth


class ViewBase:

    # helpers

    @memoize
    def _getTool(self, name):
        return getToolByName(self.context, name)

    @memoize
    def _checkPermission(self, permission):
        mtool = self._getTool('portal_membership')
        return mtool.checkPermission(permission, self.context)

    @memoize
    def _getPortalURL(self):
        utool = self._getTool('portal_url')
        return utool()

    @memoize
    def _getViewURL(self):
        return self.request['ACTUAL_URL']

    @memoize
    def _getDefaultCharset(self):
        ptool = self._getTool('portal_properties')
        return ptool.getProperty('default_charset', None)

    # interface

    @memoize
    @decode
    def title(self):
        return self.context.Title()

    @memoize
    @decode
    def description(self):
        return self.context.Description()


class FormViewBase(ViewBase):

    # helpers

    def _setRedirect(self, provider_id, action_path, keys=''):
        if provider_id == 'context':
            provider = self.context
        else:
            provider = self._getTool(provider_id)
        try:
            target = provider.getActionInfo(action_path)['url']
        except ValueError:
            target = self._getPortalURL()

        kw = {}
        message = self.request.other.get('portal_status_message', '')
        if message:
            kw['portal_status_message'] = message
        for k in keys.split(','):
            k = k.strip()
            v = self.request.form.get(k, None)
            if v:
                kw[k] = v

        query = kw and ( '?%s' % make_query(kw) ) or ''
        self.request.RESPONSE.redirect( '%s%s' % (target, query) )

        return True

    # interface

    def __call__(self, **kw):
        form = self.request.form
        for button in self._BUTTONS:
            if button['id'] in form:
                for permission in button.get('permissions', ()):
                    if not self._checkPermission(permission):
                        break
                else:
                    for transform in button.get('transform', ()):
                        status = getattr(self, transform)(**form)
                        if isinstance(status, bool):
                            status = (status,)
                        if len(status) > 1:
                            self.request.other['portal_status_message'] = status[1]
                        if not status[0]:
                            return self.index()
                    if self._setRedirect(*button['redirect']):
                        return
        return self.index()

    @memoize
    def form_action(self):
        return self._getViewURL()

    @memoize
    def listButtonInfos(self):
        form = self.request.form
        buttons = []
        for button in self._BUTTONS:
            if button.get('title', None):
                for permission in button.get('permissions', ()):
                    if not self._checkPermission(permission):
                        break
                else:
                    for condition in button.get('conditions', ()):
                        if not getattr(self, condition)():
                            break
                    else:
                        buttons.append({'name': button['id'],
                                        'value': button['title']})
        return tuple(buttons)

    @memoize
    @decode
    def listHiddenVarInfos(self):
        kw = self._getHiddenVars()
        vars = [ {'name': name, 'value': value}
                 for name, value in html_marshal(**kw) ]
        return tuple(vars)
