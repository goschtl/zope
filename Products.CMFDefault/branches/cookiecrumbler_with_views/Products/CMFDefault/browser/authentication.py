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
"""Authentication browser views.

$Id$
"""

from urllib import quote

from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zExceptions import Forbidden
from zExceptions import Redirect
from zope.app.form.browser import TextWidget
from zope.formlib import form
from zope.interface import implements
from zope.interface import Interface
from zope.schema import Bool
from zope.schema import Choice
from zope.schema import Password
from zope.schema import URI
from zope.schema.interfaces import ISource
from zope.site.hooks import getSite

from Products.CMFCore.CookieCrumbler import ATTEMPT_LOGIN
from Products.CMFCore.CookieCrumbler import ATTEMPT_NONE
from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.formlib.form import EditFormBase
from Products.CMFDefault.utils import Message as _
from Products.CMFDefault.browser.utils import ViewBase, memoize


class UnauthorizedView(BrowserView):

    """Exception view for Unauthorized.
    """

    forbidden_template = ViewPageTemplateFile('templates/forbidden.pt')

    def __call__(self):
        try:
            cctool = getToolByName(self, 'cookie_authentication')
            atool = getToolByName(self, 'portal_actions')
            target = atool.getActionInfo('user/login')['url']
        except (AttributeError, ValueError):
            # re-raise the unhandled exception
            raise self.context

        req = self.request
        attempt = getattr(req, '_cookie_auth', ATTEMPT_NONE)
        if attempt == ATTEMPT_NONE:
            # An anonymous user was denied access to something.
            retry = ''
        elif attempt == ATTEMPT_LOGIN:
            # The login attempt failed.  Try again.
            retry = '1'
        else:
            # An authenticated user was denied access to something.
            # XXX: hack context to get the right @@standard_macros/page
            #      why do we get the wrong without this hack?
            self.context = self.__parent__
            raise Forbidden(self.forbidden_template())

        if req.response.cookies.has_key(cctool.auth_cookie):
            del req.response.cookies[cctool.auth_cookie]

        came_from = req.get('came_from', None)
        if came_from is None:
            came_from = req.get('ACTUAL_URL')
            query = req.get('QUERY_STRING')
            if query:
                # Include the query string in came_from
                if not query.startswith('?'):
                    query = '?' + query
                came_from = came_from + query
        url = '%s?came_from=%s&retry=%s&disable_cookie_login__=1' % (
            target, quote(came_from), retry)
        raise Redirect(url)


class NameSource(object):

    implements(ISource)

    def __contains__(self, value):
        rich_context = getSite()
        mtool = getToolByName(rich_context, 'portal_membership')
        if mtool.getMemberById(value):
            return True
        candidates = mtool.searchMembers('email', value)
        for candidate in candidates:
            if candidate['email'].lower() == value.lower():
                return True
        return False

available_names = NameSource()


class ILoginSchema(Interface):

    """Schema for login form.
    """

    came_from = URI(
        required=False)

    name = Choice(
        title=_(u'Member ID'),
        description=_(u'Member ID or email address'),
        source=available_names)

    password = Password(
        title=_(u'Password'),
        description=_(u'Case sensitive'))

    persistent = Bool(
        title=_(u'Remember my ID.'),
        description=_(u'Saves your member ID in a cookie.'),
        default=True)


class IMailPasswordSchema(Interface):

    """Schema for mail password form.
    """

    name = Choice(
        title=_(u'Member ID'),
        description=_(u'Member ID or email address'),
        source=available_names)


class LoginFormView(EditFormBase):

    """Form view for ILoginSchema.
    """

    base_template = EditFormBase.template
    template = ViewPageTemplateFile('templates/login.pt')
    label = _(u'Log in')

    form_fields = form.FormFields(ILoginSchema)
    form_fields['name'].custom_widget = TextWidget

    actions = form.Actions(
        form.Action(
            name='login',
            label=_(u'Login'),
            success='handle_login_success',
            failure='handle_failure'))

    def setUpWidgets(self, ignore_request=False):
        cctool = self._getTool('cookie_authentication')
        ac_name = self.request.get(cctool.name_cookie)
        if ac_name and not self.request.has_key('%s.name' % self.prefix):
            self.request.form['%s.name' % self.prefix] = ac_name
        super(LoginFormView,
              self).setUpWidgets(ignore_request=ignore_request)
        self.widgets['came_from'].hide = True

    def handle_login_success(self, action, data):
        mtool = self._getTool('portal_membership')
        if not mtool.getMemberById(data['name']):
            candidates = mtool.searchMembers('email', data['name'])
            for candidate in candidates:
                if candidate['email'].lower() == data['name'].lower():
                    data['name'] = candidate['username']
                    break
        cctool = self._getTool('cookie_authentication')
        # logged_in uses default charset for decoding
        charset = self._getDefaultCharset()
        self.request.form[cctool.name_cookie] = data['name'].encode(charset)
        self.request.form[cctool.pw_cookie] = data['password'].encode(charset)
        self.request.form[cctool.persist_cookie] = data['persistent']
        cctool(self.context, self.request)
        return self._setRedirect('portal_actions', 'user/logged_in',
                                 '%s.came_from' % self.prefix)


class MailPasswordFormView(EditFormBase):

    """Form view for IMailPasswordSchema.
    """

    base_template = EditFormBase.template
    template = ViewPageTemplateFile('templates/mail_password.pt')
    label = _(u"Don't panic!")
    description = _(u"Just enter your member ID below, click 'Send', and "
                    u"your password will be mailed to you if you gave a "
                    u"valid email address when you signed on.")

    form_fields = form.FormFields(IMailPasswordSchema)
    form_fields['name'].custom_widget = TextWidget

    actions = form.Actions(
        form.Action(
            name='send',
            label=_(u'Send'),
            success='handle_send_success',
            failure='handle_failure'))

    def setUpWidgets(self, ignore_request=False):
        cctool = self._getTool('cookie_authentication')
        ac_name = self.request.get(cctool.name_cookie)
        if ac_name and not self.request.has_key('%s.name' % self.prefix):
            self.request.form['%s.name' % self.prefix] = ac_name
        super(MailPasswordFormView,
              self).setUpWidgets(ignore_request=ignore_request)

    def handle_send_success(self, action, data):
        mtool = self._getTool('portal_membership')
        if not mtool.getMemberById(data['name']):
            candidates = mtool.searchMembers('email', data['name'])
            for candidate in candidates:
                if candidate['email'].lower() == data['name'].lower():
                    data['name'] = candidate['username']
                    break
        rtool = self._getTool('portal_registration')
        rtool.mailPassword(data['name'], self.request)
        self.status = _(u'Your password has been mailed to you.')
        return self._setRedirect('portal_actions', 'user/login')


class Logout(ViewBase):
    """Log the user out"""
    
    @memoize
    def logged_in(self):
        """Check whether the user is (still logged in)"""
        mtool = self._getTool('portal_membership')
        return mtool.isAnonymousUser()
        
    @memoize
    def logout(self):
        """Log the user out"""
        cctool = self._getTool('cookie_authentication')
        cctool.logout(self.request.response)
    
    @memoize    
    def clear_skin_cookie(self):
        """Remove skin cookie"""
        stool = self._getTool('portal_skins')
        stool.clearSkinCookie()
    
    def __call__(self):
        """Clear cookies and return the template"""
        self.clear_skin_cookie()
        self.logout()
        return super(Logout, self).__call__()
