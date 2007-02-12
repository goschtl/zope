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
"""Search Filter Browser View

$Id$
"""
import persistent.dict
import zope.component
import zope.interface
import zope.schema

from hurry import query
from z3c.searchfilter import interfaces
from zope.app.form.browser import RadioWidget
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.app.session.interfaces import ISession
from zope.formlib import form
from zope.index.text import parsetree
from zope.location import location
from zope.traversing import api

from z3c.searchfilter import criterium
from z3c.searchfilter.interfaces import _


FILTER_KEY = 'z3c.searchfilter.filter'


def ConnectorWidget(context, request):
    return RadioWidget(context, context.vocabulary, request)

class BaseCriteriumRow(form.SubPageForm):

    template = ViewPageTemplateFile('criterium_row.pt')
    actions = form.Actions()

    def setUpWidgets(self, ignore_request=False):
        self.adapters = {}
        self.widgets = form.setUpEditWidgets(
            self.form_fields, self.prefix, self.context, self.request,
            adapters=self.adapters, ignore_request=ignore_request
            )

    def save(self):
        data = {}
        form.getWidgetsData(self.widgets, self.prefix, data)
        form.applyChanges(self.context, self.form_fields, data, self.adapters)


class FullTextCriteriumRow(BaseCriteriumRow):

    form_fields = form.FormFields(
        interfaces.IFullTextCriterium).select('value')


class Filter(form.SubPageForm):

    prefix = 'filters.'
    form_fields = form.FormFields(interfaces.ISearchCriteria)
    form_fields['connector'].custom_widget = ConnectorWidget

    template = ViewPageTemplateFile('filter.pt')
    criteriumRows = None

    # Must be implemented by sub-class or instance
    criteriaClass = None

    # The filter name is used in the session to identify the type of filter
    filterName = 'criteria'

    # The context name is used in addition to the filter name to identify one
    # filter for one specific context.
    @property
    def contextName(self):
        return api.getName(self.context)

    @property
    def criteria(self):
        session = ISession(self.request)
        filters = session[FILTER_KEY]

        filter = filters.get(self.filterName)
        if filter is None:
            # smells like we have to take care on references in this dict!
            filters[self.filterName] = persistent.dict.PersistentDict()
            filter = filters[self.filterName]

        # Note, the context reference has to be deleted if we delete the
        # context
        criteria = filter.get(self.contextName)
        if criteria is None:
            criteria = filter[self.contextName] = self.criteriaClass()
            # Locate the search criteria on the context, so that security does
            # not get lost
            location.locate(criteria, self.context, self.contextName)
        return criteria

    def values(self):
        queries = []
        # Generate the query
        queries.append(self.criteria.generateQuery())
        # Return the results
        try:
            return query.query.Query().searchResults(query.And(*queries))
        except TypeError:
            self.status = _('One of the criteria is setup improperly.')
        except parsetree.ParseError, error:
            self.status = _('Invalid search text.')
        # Return an empty set, since an error must have occurred
        return []

    def available(self):
        for name, factory in self.criteria.available():
            yield {'name': name, 'title': factory.title}

    def _createCriteriumRows(self):
        self.criteriumRows = []
        index = 0
        for criterium in self.criteria:
            row = zope.component.getMultiAdapter(
                (criterium, self.request), name='row')
            row.setPrefix(str(index))
            row.update()
            self.criteriumRows.append(row)
            index += 1

    def update(self):
        # Make sure the criteria get updated
        self._createCriteriumRows()
        # Execute actions
        super(Filter, self).update()

    @form.action(_('Filter'))
    def handleFilter(self, action, data):
        if 'connector' in data:
            self.criteria.connector = data['connector']
        for row in self.criteriumRows:
            row.save()

    @form.action(_('Add'))
    def handleAdd(self, action, data):
        name = self.request.form[self.prefix + 'newCriterium']
        self.criteria.add(name)
        self._createCriteriumRows()
        self.status = _('New criterium added.')

    @form.action(_('Clear'))
    def handleClear(self, action, data):
        self.criteria.clear()
        self._createCriteriumRows()
        self.status = _('Criteria cleared.')

    def render(self):
        return self.template()
