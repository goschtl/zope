##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
"""
$Id:$
"""
__docformat__ = "reStructuredText"

import zope.component
import zope.event
import zope.lifecycleevent

from zope.index.text import parsetree
from zope.location import location

from z3c.indexer.search import SearchQuery
from z3c.template.template import getPageTemplate
from z3c.template.template import getLayoutTemplate

from z3c.form.interfaces import IWidgets
from z3c.form import button
from z3c.form import field
from z3c.form import form
from z3c.formui import form as formui
from z3c.form.browser.radio import RadioFieldWidget
from z3c.searcher import interfaces
from z3c.searcher.interfaces import _
from z3c.searcher import criterium
from z3c.searcher import filter


class CriteriumForm(form.Form):

    formErrorsMessage = _('There were some errors.')
    successMessage = _('Data successfully updated.')
    noChangesMessage = _('No changes were applied.')

    fields = field.Fields(interfaces.ISearchCriterium).select('connectorName',
        'value')
    fields['connectorName'].widgetFactory = RadioFieldWidget

    def updateWidgets(self):
        self.widgets = zope.component.getMultiAdapter(
            (self, self.request, self.getContent()), IWidgets)
        self.widgets.update()

    @property
    def criteriumName(self):
        return self.context.__name__

    def save(self):
        data, errors = self.widgets.extract()
        if errors:
            self.status = self.formErrorsMessage
            return
        content = self.getContent()
        changed = form.applyChanges(self, content, data)
        if changed:
            zope.event.notify(
                zope.lifecycleevent.ObjectModifiedEvent(content))
            self.status = self.successMessage
        else:
            self.status = self.noChangesMessage

    @button.buttonAndHandler(_('Remove'), name='remove')
    def handleRemove(self, data):
        searchFilter = self.context.__parent__
        searchFilter.removeCriterium(self.context)
        self.request.response.redirect(self.request.getURL())


class TextCriteriumForm(CriteriumForm):

    fields = field.Fields(interfaces.ITextCriterium).select('connectorName',
        'value')
    fields['connectorName'].widgetFactory = RadioFieldWidget


class FilterForm(form.Form):
    """Filter form."""

    zope.interface.implements(interfaces.IFilterForm)

    # default form vars
    prefix = 'filterform'
    ignoreContext = True
    criteriumRows = []
    searchFilter = None

    # The filterName is used in the ISearchSession to identify filter
    filterName = 'searchFilter'

    # will probably get overriden by the parent form
    filterFactory = filter.SearchFilter

    # customization hooks
    @property
    def filterKey(self):
        """Return the default filter key.
        
        You can override this method and use a KeyReference intid if you need
        different filters for each context.
        """
        return interfaces.SEARCH_SESSION_FILTER_KEY

    def criteriumFactories(self):
        for name, factory in self.searchFilter.criteriumFactories:
            yield {'name': name, 'title': factory.title}

    @property
    def searchFilter(self):
        session = interfaces.ISearchSession(self.request)
        searchFilter = session.getFilter(self.filterName, self.filterKey)
        if searchFilter is None:
            searchFilter = self.filterFactory()
            session.addFilter(self.filterName, searchFilter, self.filterKey)
            # Locate the search filter, so that security does not get lost
            location.locate(searchFilter, self.context, self.filterName)
        return searchFilter

    def values(self):
        # TODO: implement better error handling and allow to register error
        # views for unknown index search error. Right now we only catch some
        # known search index errors.
        try:
            # generate the search query
            searchQuery = self.searchFilter.generateQuery()
            # return result
            return SearchQuery(searchQuery).searchResults()
        except TypeError:
            self.status = _('One of the search filter is setup improperly.')
        except parsetree.ParseError, error:
            self.status = _('Invalid search text.')
        # Return an empty result, since an error must have occurred
        return []

    def setupCriteriumRows(self):
        self.criteriumRows = []
        append = self.criteriumRows.append
        index = 0
        for criterium in self.searchFilter.criteria:
            row = zope.component.getMultiAdapter(
                (criterium, self.request), name='row')
            row.prefix = str(index)
            row.update()
            append(row)
            index += 1

    def update(self):
        self.setupCriteriumRows()
        super(FilterForm, self).update()

    @button.buttonAndHandler(u'Add')
    def handleAdd(self, action):
        name = self.request.get(self.prefix + 'newCriterium', None)
        if name is not None:
            self.searchFilter.createAndAddCriterium(name)
            self.setupCriteriumRows()
            self.status = _('New criterium added.')

    @button.buttonAndHandler(u'Clear', name='clear')
    def handleClear(self, action):
        self.searchFilter.clear()
        self.setupCriteriumRows()
        self.status = _('Criteria cleared.')

    @button.buttonAndHandler(u'Search', name='search')
    def handleSearch(self, action):
        data, errors = self.widgets.extract()
        for row in self.criteriumRows:
            row.save()


class SearchForm(formui.Form):
    """Search form using a sub form for offering filters.
    
    Note this form uses the layout/content template pattern by default.
    And the content template renders the search filter into the ``extra-info```
    slot offered from z3c.formui ``form`` macro
    """

    zope.interface.implements(interfaces.ISearchForm)

    template  = getPageTemplate()
    values = []
    filterFactory = filter.SearchFilter

    def setupFilterForm(self):
        """Setup filter form before super form get updated."""
        self.filterForm = FilterForm(self.context, self.request)
        self.filterForm.filterFactory = self.filterFactory

    def updateFilterForm(self):
        """Update filter form after super form get updated."""
        self.filterForm.update()
        self.values = self.filterForm.values()

    def update(self):
        # setup filter form
        self.setupFilterForm()
        # process super form
        super(SearchForm, self).update()
        # process filter form
        self.updateFilterForm()
