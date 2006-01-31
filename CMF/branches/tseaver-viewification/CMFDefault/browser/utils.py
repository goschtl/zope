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

from ZTUtils import Batch
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


class BatchViewBase(ViewBase):

    # helpers

    _BATCH_SIZE = 25

    @memoize
    def _getBatchStart(self):
        return self.request.form.get('b_start', 0)

    @memoize
    def _getBatchObj(self):
        b_start = self._getBatchStart()
        items = self._getItems()
        return Batch(items, self._BATCH_SIZE, b_start, orphan=0)

    @memoize
    def _getNavigationURL(self, b_start):
        target = self._getViewURL()
        kw = self._getHiddenVars()

        kw['b_start'] = b_start
        for k, v in kw.items():
            if not v or k == 'portal_status_message':
                del kw[k]

        query = kw and ('?%s' % make_query(kw)) or ''
        return u'%s%s' % (target, query)

    # interface

    @memoize
    def navigation_previous(self):
        batch_obj = self._getBatchObj().previous
        if batch_obj is None:
            return None

        length = len(batch_obj)
        url = self._getNavigationURL(batch_obj.first)
        if length == 1:
            title = _(u'Previous item')
        else:
            title = _(u'Previous ${count} items', mapping={'count': length})
        return {'title': title, 'url': url}

    @memoize
    def navigation_next(self):
        batch_obj = self._getBatchObj().next
        if batch_obj is None:
            return None

        length = len(batch_obj)
        url = self._getNavigationURL(batch_obj.first)
        if length == 1:
            title = _(u'Next item')
        else:
            title = _(u'Next ${count} items', mapping={'count': length})
        return {'title': title, 'url': url}
