""" Browser views for CMFDefault.Link.Link

$Id$
"""

from urllib import quote

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

from Products.CMFDefault.utils import MessageID as _
from Products.CMFCore.permissions import View
from Products.CMFCore.permissions import ModifyPortalContent

from Products.Five import BrowserView
from Products.PageTemplates.PageTemplate import PageTemplate

_LINK_DISPLAY_TEMPLATE = """\
<p i18n:translate="">Link:
 <a href="" alt="TITLE"
    tal:attributes="href options/remote_url;
                    alt options/title;
                   "
    tal:content="options/remote_url"
    i18n:name="link">http://www.example.com/</a>
</p>
"""

_BUTTONS = {
    'change':
        {'value': _('Change'),
         'redirect' : 'edit.html',
        },
    'change_and_view':
        {'value': _('Change and View'),
         'redirect': 'view.html',
        },
}

_BUTTON_NAMES = ('change', 'change_and_view')

class LinkDisplayView(BrowserView):

    security = ClassSecurityInfo()

    def __init__(self, context, request):
        self.context = context
        self.request = request

    _link_display_template = PageTemplate()
    _link_display_template.write(_LINK_DISPLAY_TEMPLATE)

    security.declareProtected(View, 'renderContent')
    def renderContent(self):
        return self._link_display_template( remote_url=self.context.getRemoteUrl()
                                          , title=self.context.title
                                          )

InitializeClass(LinkDisplayView)

_LINK_EDITING_TEMPLATE = """\
<form action="edit.py" method="post">
  <table class="FormLayout">
    <tr>
      <th i18n:translate="">Title</th>
      <td tal:content="options/title">Title</td>
    </tr>
    <tr>
      <th i18n:translate="">URL</th>
      <td>
        <input type="text" name="remote_url" size="40" value=""
               tal:attributes="value options/remote_url" />
      </td>
    </tr>
    <tr>
      <td></td>
      <td class="FormButtons">
        <tal:loop tal:repeat="button options/buttons"
          ><input type="submit" name="ButtonName" value="ButtonValue"
                  tal:attributes="name button/name;
                                  value button/value;
                                 "
                  i18n:attributes="value" /></tal:loop>
      </td>
    </tr>
  </table>
</form>
"""

class LinkEditingView(BrowserView):

    security = ClassSecurityInfo()

    def __init__(self, context, request):
        self.context = context
        self.request = request

    _link_editing_template = PageTemplate()
    _link_editing_template.write(_LINK_EDITING_TEMPLATE)

    security.declareProtected(View, 'renderContent')
    def renderContent(self):
        buttons = [{'name': name, 'value': _BUTTONS[name]['value']}
                       for name in _BUTTON_NAMES]
        remote_url = self.context.getRemoteUrl()

        return self._link_editing_template( remote_url=remote_url
                                          , title=self.context.Title()
                                          , buttons=buttons
                                          )

    security.declareProtected(ModifyPortalContent, 'update')
    def update(self, form):
        self.context.edit(form.get('remote_url', ''))

    security.declareProtected(ModifyPortalContent, 'controller')
    def controller(self, RESPONSE):
        """ Process a form post and redirect, if needed.
        """
        context = self.context
        form = self.request.form
        for button in _BUTTONS.keys():
            if button in form:
                self.update(form)
                goto = '%s/%s' % ( context.absolute_url()
                                 , _BUTTONS[button]['redirect']
                                 )
                qs = 'portal_status_message=%s' % quote('Link updated.')
                RESPONSE.redirect('%s?%s' % (goto, qs))
                return

        return self.index()
    
InitializeClass(LinkEditingView)

#
#   XXX:  Try out Yuppie's style here
#
import urlparse

from Products.CMFDefault.exceptions import ResourceLockedError
from Products.CMFDefault.utils import MessageID as _

from utils import decode
from utils import FormViewBase
from utils import memoize


class IllegalURL(ValueError):
    pass


class LinkEditView(FormViewBase):

    """ Edit view for IMutableLink.
    """

    _BUTTONS = ({'id': 'change',
                 'title': _(u'Change'),
                 'transform': ('validateURL', 'link_edit_control'),
                 'redirect': ('context', 'object/edit'),
                },
                {'id': 'change_and_view',
                 'title': _(u'Change and View'),
                 'transform': ('validateURL', 'link_edit_control'),
                 'redirect': ('context', 'object/view'),
                },
               )

    # helpers

    @memoize
    def _normalizeURL(self, remote_url):
        tokens = urlparse.urlparse( remote_url, 'http' )
        if tokens[0] == 'http':
            if tokens[1]:
                # We have a nethost. All is well.
                url = urlparse.urlunparse(tokens)
            elif tokens[2:] == ('', '', '', ''):
                # Empty URL
                url = ''
            else:
                # Relative URL, keep it that way, without http:
                tokens = ('', '') + tokens[2:]
                url = urlparse.urlunparse(tokens)
        else:
            # Other scheme, keep original
            url = urlparse.urlunparse(tokens)
        return url

    # interface

    @memoize
    @decode
    def remote_url(self):
        return self.request.form.get('remote_url', self.context.remote_url)

    # validators

    def validateURL(self, remote_url='', **kw):
        try:
            remote_url = self._normalizeURL(remote_url)
        except IllegalURL, errmsg:
            return False, errmsg
        else:
            self.request.form[remote_url] = remote_url
            return True

    # controllers

    def link_edit_control(self, remote_url, **kw):
        context = self.context
        if remote_url != context.remote_url:
            try:
                context.edit(remote_url=remote_url)
                return True, _(u'Link changed.')
            except ResourceLockedError, errmsg:
                return False, errmsg
        else:
            return False, _(u'Nothing to change.')
