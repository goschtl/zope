##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Browser View Components for Bug Trackers

$Id: tracker.py,v 1.13 2004/03/18 18:04:54 philikon Exp $
"""
from zope.app import zapi
from zope.app.container.browser.adding import Adding
from zope.app.dublincore.interfaces import IZopeDublinCore
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.schema.vocabulary import getVocabularyRegistry

from bugtracker import TrackerMessageID as _
from bugtracker.batching import Batch
from bugtracker.browser.bug import BugBaseView
from bugtracker.interfaces import IStatusVocabulary, IReleaseVocabulary
from bugtracker.interfaces import IPriorityVocabulary, IBugTypeVocabulary
from bugtracker.interfaces import IComment
from bugtracker.interfaces import ISearchableText


class BugTrackerAdding(Adding):
    """Custom adding view for NewsSite objects."""

    def add(self, content):
        self.context['dummy'] = content
        self.contentName = zapi.name(content)
        return self.context[name]


class AddBugTracker(object):
    """Add a bug tracker."""

    def createAndAdd(self, data):
        content = super(AddBugTracker, self).createAndAdd(data)

        if self.request.get('setup_vocabs'):
            vocab = IStatusVocabulary(content)
            vocab.add('new', _('New'), True)
            vocab.add('open', _('Open'))
            vocab.add('assigned', _('Assigned'))
            vocab.add('deferred', _('Deferred'))
            vocab.add('closed', _('Closed'))
            vocab = IBugTypeVocabulary(content)
            vocab.add('bug', _('Bug'), True)
            vocab.add('feature', _('Feature'))
            vocab.add('release', _('Release'))
            vocab = IReleaseVocabulary(content)
            vocab.add('None', _('(not specified)'), True)
            vocab = IPriorityVocabulary(content)
            vocab.add('low', _('Low'))
            vocab.add('normal', _('Normal'), True)
            vocab.add('urgent', _('Urgent'))
            vocab.add('critical', _('Critical'))

        return content


class Settings(object):
    """Change the settings of the Bug Tracker."""

    # list of managable vocabulary interfaces that we want to have
    ifaces = [IStatusVocabulary, IReleaseVocabulary,
              IPriorityVocabulary, IBugTypeVocabulary]

    def getManagableVocabularyViews(self):
        return map(lambda iface:
                   ManagableVocabularyView(self.context, self.request, iface),
                   self.ifaces)

    def addValue(self, iface, value, title):
        iface = filter(lambda i: i.getName() == iface, self.ifaces)[0]
        vocab = ManagableVocabularyView(self.context, self.request, iface)
        vocab.addValue(value, title)

    def deleteValues(self, iface, values):
        iface = filter(lambda i: i.getName() == iface, self.ifaces)[0]
        vocab = ManagableVocabularyView(self.context, self.request, iface)
        vocab.deleteValues(values)

    def setDefaultValue(self, iface, values):
        iface = filter(lambda i: i.getName() == iface, self.ifaces)[0]
        vocab = ManagableVocabularyView(self.context, self.request, iface)
        vocab.setDefault(values[0])


class ManagableVocabularyView(object):

    def __init__(self, context, request, vocab_iface):
        self.context = context
        self.request = request
        self.vocab_iface = vocab_iface

    def getExistingValues(self):
        vocab = self.vocab_iface(self.context)
        return iter(vocab)

    def addValue(self, value, title):
        vocab = self.vocab_iface(self.context)
        vocab.add(value, title)
        return self.request.response.redirect('./@@settings.html')

    def deleteValues(self, values):
        vocab = self.vocab_iface(self.context)
        for value in values:
            vocab.delete(value)
        return self.request.response.redirect('./@@settings.html')

    def title(self):
        vocab = self.vocab_iface(self.context)
        return vocab.title

    def default(self):
        vocab = self.vocab_iface(self.context)
        return vocab.default

    def setDefault(self, value):  
        vocab = self.vocab_iface(self.context)
        vocab.default = value
        return self.request.response.redirect('./@@settings.html')


def checkBug(bug, criteria, search_text):
    for name, values in criteria:
        if name is 'owners':
            if values and not filter(lambda u: u in bug.owners, values):
                return False
        else:
            if values and not getattr(bug, name) in values:
                return False

    # TODO: Extremely crude text search; should use indexes
    text = ' '.join(ISearchableText(bug).getSearchableText())
    if search_text != '':
        terms = search_text.split(' ')
        for term in terms:
            if not term in text:
                return False
        
    return True


class BugView(BugBaseView):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def numberOfComments(self):
        return len(filter(IComment.isImplementedBy, self.context.values()))

    def name(self):
        return zapi.name(self.context)

    def descriptionPreview(self):
        if len(self.context.description) < 200:
            return self.context.description
        else:
            return self.context.description[:200] + u'...'

    def shortCreated(self):
        return self.created().split()[0]


class Overview(object):
    """Overview of all the bugs."""

    bug_listing_normal = ViewPageTemplateFile('bug_listing_normal.pt')
    bug_listing_compressed = ViewPageTemplateFile('bug_listing_compressed.pt')

    # Tuple values:
    #   - collection name
    #   - Vocabulary Registry name
    #   - Display Title
    #   - bug attribute name
    filter_vars = (('stati', 'Stati', 'Status', 'status'),
                   ('types', 'BugTypes', 'Type', 'type'),
                   ('releases', 'Releases', 'Release', 'release'),
                   ('priorities', 'Priorities', 'Priority', 'priority'),
                   ('owners', 'Users', 'Owners', 'owners'),
                   )

    def getBugs(self):
        """Return a list of all bugs having a status listed in the parameter.

        If the parameter is an empty list/tuple, then show all bugs.
        """
        if hasattr(self, '_bugs'):
            return self._bugs

        criteria = []
        for collName, dummy1, dummy2, name in self.filter_vars:
            raw = self.request.cookies.get('filter_'+collName, "")
            criteria.append((name, raw != "" and raw.split(", ") or []))
        
        formatter = self.request.locale.dates.getFormatter('dateTime', 'short')
        result = []
        for name, bug in self.context.items():
            if checkBug(bug, criteria, self.getSearchText()):
                result.append(BugView(bug, self.request))


        start = int(self.request.get('start', 0))
        size = int(self.request.get('size', 20))
                
        self._bugs = Batch(result, start, size)
        return self._bugs

    def updateSettings(self):
        for collName, dummy1, dummy2, dummy3 in self.filter_vars:
            values = self.request.get(collName, [])
            self.request.response.setCookie('filter_'+collName,
                                            ', '.join(values))
        self.setSearchText()
        self.setViewType()
        self.setShowFilterOptions()
        return self.request.response.redirect('./overview.html')

    def getSettingsInfo(self):
        registry = getVocabularyRegistry()
        info = []
        for varname, vocname, title, dummy in self.filter_vars:
            raw = self.request.cookies.get('filter_'+varname, "")
            info.append({'setting': raw != "" and raw.split(", ") or [],
                         'all': iter(registry.get(self.context, vocname)),
                         'title': title,
                         'name': varname})
        return info
            
    def getSearchText(self):
        return self.request.cookies.get('search_text', '')

    def setSearchText(self):
        value = self.request.get('search_text', '')
        self.request.response.setCookie('search_text', value)

    def getViewType(self):
        return self.request.cookies.get('view_type', 'normal')

    def setViewType(self):
        value = self.request.get('view_type', 'normal')
        self.request.response.setCookie('view_type', value)

    def getShowFilterOptions(self):
        return int(self.request.cookies.get('show_filter_options', '1'))

    def setShowFilterOptions(self):
        if 'COLLAPSE' in self.request:
            value = '0'
        else:
            value = '1'
        self.request.response.setCookie('show_filter_options', value)

    def numberOfBugs(self):
        return len(self.context)
