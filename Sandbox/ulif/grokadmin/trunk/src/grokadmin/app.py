##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
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
"""The Grok Administration and Development UI"""

import zope.component

from zope.app.broken.broken import IBroken
from zope.interface import Interface
from ZODB.broken import Broken

import grok

grok.define_permission('grok.ManageApplications')

class GrokAdmin(grok.Application, grok.Container):
    """The Grok Administrators and Developers UI.

    We can create a ``GrokAdmin`` application::

       >>> from grokadmin.app import GrokAdmin
       >>> admin = GrokAdmin()
       >>> admin
       <grokadmin.app.GrokAdmin object at 0x...>
       
    """


class Index(grok.View):
    """A redirector to the real frontpage.
    """
    grok.name('index')
    grok.require('grok.ManageApplications')

    def render(self):
        # Go to the first page immediately.
        self.redirect(self.url('applications'))


class GrokAdminMacros(grok.View):
    """Provides the o-wrap layout."""
    grok.context(Interface)


class Applications(grok.View):
    """View for application management.

    """
    grok.name('applications')
    grok.require('grok.ManageApplications')

    def getDocOfApp(self, apppath, headonly = True):
        return ""
        # XXX Reactivate docfinder...
        doctor = docgrok.docgrok_handle(apppath)
        result = doctor.getDoc(headonly)
        if result is None:
            result = ""
        return result

    def update(self):
        # Available apps...
        apps = zope.component.getAllUtilitiesRegisteredFor(
            grok.interfaces.IApplication)
        apps_folder = get_apps_folder(self.context)
        self.applications = (
            {'name': "%s.%s" % (x.__module__, x.__name__),
             'docurl':("%s.%s" % (x.__module__, x.__name__)).replace('.', '/')}
            for x in apps)

        # Installed apps...
        inst_apps = [x for x in apps_folder.values()
                     if hasattr(x, '__class__') and x.__class__ in apps
                     and not issubclass(x.__class__, Broken)]
        inst_apps.sort(lambda x, y: cmp(x.__name__, y.__name__))
        self.installed_applications = inst_apps

        # Broken apps...
        broken_apps = [{'obj':y, 'name':x} for x,y in apps_folder.items()
                       if isinstance(y, Broken)]
        broken_apps.sort(lambda x, y: cmp(x['name'], y['name']))
        self.broken_applications = broken_apps


class Add(grok.View):
    """Add an application.
    """
    grok.require('grok.ManageApplications')

    def update(self, inspectapp=None, application=None):
        if inspectapp is not None:
            self.redirect(self.url("docgrok") + "/%s/index"%(
                application.replace('.','/'),))
        return

    def render(self, application, name, inspectapp=None):
        if name is None or name == "":
            self.redirect(self.url(self.context))
            return
        if name is None or name == "":
            self.redirect(self.url(self.context))
            return
        app = zope.component.getUtility(grok.interfaces.IApplication,
                                        name=application)
        try:
            apps_folder = get_apps_folder(self.context)
            apps_folder[name] = app()
            self.flash(u'Added %s `%s`.' % (application, name))
        except DuplicationError:
            self.flash(
                u'Name `%s` already in use. Please choose another name.' % (
                name,))
        self.redirect(self.url(self.context))


def get_apps_folder(context):
    """Return a folder where apps can be added for a context.

    For contexts, that have no parent, we return the context itself::
    
       >>> from grokadmin.app import get_apps_folder
       >>> from grokadmin.app import GrokAdmin
       >>> admin = GrokAdmin()
       >>> first_folder = get_apps_folder(admin)
       >>> first_folder
       <grokadmin.app.GrokAdmin object at 0x...>

       >>> first_folder is admin
       True
       
    For contexts, that _have_ a parent, that parent is returned::

       >>> admin2 = GrokAdmin()
       >>> admin['subadmin'] = admin2
       >>> second_folder = get_apps_folder(admin2)
       >>> second_folder is first_folder
       True

    We only 'go up' one level::

       >>> admin3 = GrokAdmin()
       >>> admin2['subsubadmin'] = admin3
       >>> third_folder = get_apps_folder(admin3)
       >>> third_folder is admin2
       True
       
    
    """
    if getattr(context, '__parent__', None) is None:
        return context
    return context.__parent__

