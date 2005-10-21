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
""" Metadata view class

$Id$
"""
from Globals import InitializeClass
from Products.Five.browser import BrowserView
from Products.CMFCore.interfaces import IDublinCore
from Products.CMFCore.interfaces import ICatalogableDublinCore
from Products.CMFCore.utils import getToolByName

from Products.CMFDefault.utils import MessageID as _

_DC_NAMES = IDublinCore.names()
_CDC_NAMES = ICatalogableDublinCore.names()

_BUTTONS = {
    'change':
        {'value': _('Change'),
         'redirect' : 'metadata.html',
        },
    'change_and_edit':
        {'value': _('Change and Edit'),
         'redirect': 'edit.html',
        },
    'change_and_view':
        {'value': _('Change and View'),
         'redirect': 'view.html',
        },
}

_BUTTON_NAMES = ('change', 'change_and_edit', 'change_and_view')

def _tuplify( value ):

    if isinstance(value, basestring):
        value = (value,)
    elif not isinstance(value, tuple):
        value = tuple(value)

    return tuple(filter(None, value))

class MetadataView(BrowserView):

    def getMetadataInfo(self):
        """ Return a mapping describing all our context's metadata.
        """
        result = {}
        context = self.context

        for name in _DC_NAMES + _CDC_NAMES:

            if name.startswith('list'):
                key = name[4:]
            elif name == 'Contributors':
                key = name
                name = 'listContributors'
            else:
                key = name

            result[key] = getattr(context, name)()

        return result

    def getFormInfo(self):
        """ Return a mapping describing all our context formstate.
        """
        result = {}
        context = self.context
        result['allow_discussion'] = getattr(context, 'allow_discussion', None)
        result['subject_lines'] = '\n'.join(context.Subject())
        result['contributor_lines'] = '\n'.join(context.listContributors())
        result['buttons'] = [{'name': name, 'value': _BUTTONS[name]['value']}
                                for name in _BUTTON_NAMES]
        return result

    def update(self, form):
        context = self.context
        dtool = getToolByName(context, 'portal_discussion', None)

        if 'title' in form:
            context.setTitle(form['title'])

        if 'description' in form:
            context.setDescription(form['description'])

        if 'subject' in form:
            context.setSubject(_tuplify(form['subject']))

        if 'contributors' in form:
            context.setContributors(_tuplify(form['contributors']))

        if 'effective_date' in form:
            context.setEffectiveDate(form['effective_date'])

        if 'expiration_date' in form:
            context.setExpirationDate(form['expiration_date'])

        if 'format' in form:
            context.setFormat(form['format'])

        if 'language' in form:
            context.setLanguage(form['language'])

        if 'rights' in form:
            context.setRights(form['rights'])

        if dtool and 'allow_discussion' in form:
            allow_discussion = form['allow_discussion']
            if allow_discussion == 'default':
                allow_discussion = None
            elif allow_discussion == 'off':
                allow_discussion = False
            elif allow_discussion == 'on':
                allow_discussion = True
            dtool.overrideDiscussionFor(context, allow_discussion)
            
    def controller(self, RESPONSE):
        """ Process a form post and redirect, if needed.
        """
        context = self.context
        form = self.request.form
        for button in _BUTTONS.keys():
            if button in form:
                self.update(form)
                redirect = _BUTTONS[button]['redirect']
                RESPONSE.redirect('%s/%s' % (context.absolute_url(), redirect))
                return

        return self.index()

