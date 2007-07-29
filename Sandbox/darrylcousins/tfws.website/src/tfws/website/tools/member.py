from urllib import urlencode

import zope.interface
from zope.traversing.browser import absoluteURL
from zope.app.component import hooks
from zope.app.security.interfaces import IUnauthenticatedPrincipal

import grok

import mars.viewlet
import mars.template

import mars.layer

from tfws.website.layer import IWebSiteLayer
from tfws.website import tools
from tfws.website.i18n import MessageFactory as _

mars.layer.layer(IWebSiteLayer)

class MemberTool(mars.viewlet.Viewlet):
    """A viewlet that has its own template"""
    grok.context(zope.interface.Interface) # maybe IContent?
    mars.viewlet.manager(tools.ITools)
    weight = 1

    @property
    def menu(self):
        """Return menu item entries in a TAL-friendly form."""
        result = []

        principal = getattr(self.request, 'principal', None)
        if not principal:
            return result

        if IUnauthenticatedPrincipal.providedBy(principal):
            return self.getUnauthenticatedMenu()
        else:
            return self.getAuthenticatedMenu()

    def getUnauthenticatedMenu(self):
        result = []

        request_url = self.request.getURL()
        site_url = absoluteURL(hooks.getSite(), self.request)

        action = site_url + '/login'
        fullaction = '%s?%s' % (action, urlencode({'camefrom': request_url}))
        result.append(
            {'title': _("Login"),
             'action': fullaction,
             'description': _("Login"),
             'selected': request_url.endswith(action) and u'selected' or u''
            })
    
        return result

    def getAuthenticatedMenu(self):
        result = []

        request_url = self.request.getURL()
        site_url = absoluteURL(hooks.getSite(), self.request)

        action = site_url + '/logout'
        fullaction = '%s?%s' % (action, urlencode({'camefrom': request_url}))
        result.append(
            {'title': _("Logout"),
             'action': fullaction,
             'description': _("Logout"),
             'selected': u''
            })
    
        action = site_url + '/edit-account'
        result.append(
            {'title': _("Edit Account"),
             'action': action,
             'description': _("Edit user account"),
             'selected': request_url.endswith(action) and u'selected' or u''
            })
    
        action = site_url + '/account'
        result.append(
            {'title': _("Account"),
             'action': action,
             'description': _("User account"),
             'selected': request_url.endswith(action) and u'selected' or u''
            })
    
        return result

class MemberToolTemplate(mars.template.TemplateFactory):
    grok.template('member.pt')
    grok.context(MemberTool)
