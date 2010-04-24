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
$Id$
"""
__docformat__ = "reStructuredText"
import zope.interface
from zope.traversing.browser import absoluteURL
from zope.viewlet.viewlet import CSSViewlet
from z3c.pagelet import browser
from z3c.form import button, field, form, group, widget
from zc.table import column

from z3c.formdemo.browser import formatter
from z3c.formdemo.questionnaire import interfaces, questionnaire
from z3c.formui import layout

QuestionnaireCSSViewlet = CSSViewlet('questionnaire.css')

class IQuestionnaireGroup(zope.interface.Interface):
    """Questionnaire Group"""

class IQuestionnairePage(zope.interface.Interface):
    """Questionnaire Page"""


class DevelopmentExperienceGroup(group.Group):
    zope.interface.implements(IQuestionnaireGroup)
    label = u'Development Experience'
    fields = field.Fields(interfaces.IQuestionnaire).select(
        'zope2', 'plone', 'zope3', 'five')


class ContributorExperienceGroup(group.Group):
    zope.interface.implements(IQuestionnaireGroup)
    label = u'Contributor Experience'
    fields = field.Fields(interfaces.IQuestionnaire).select(
        'contributor', 'years', 'zopeId')


class QuestionnaireAddForm(layout.AddFormLayoutSupport,
                          group.GroupForm, form.AddForm):
    zope.interface.implements(IQuestionnairePage)

    label = u'Zope Developer Questionnaire'
    fields = field.Fields(interfaces.IQuestionnaire).select('name', 'age')
    groups = (DevelopmentExperienceGroup, ContributorExperienceGroup)

    def create(self, data):
        return questionnaire.Questionnaire(**data)

    def add(self, object):
        count = 0
        while 'questionnaire-%i' %count in self.context:
            count += 1;
        self._name = 'questionnaire-%i' %count
        self.context[self._name] = object
        return object

    def nextURL(self):
        url = absoluteURL(self.context, self.request)
        return url + '/questionnaireResults.html'

SubmitLabel = button.StaticButtonActionAttribute(
    u'Submit Questionnaire', button=form.AddForm.buttons['add'],
    form=QuestionnaireAddForm)


def getDescriptionAsLabel(value):
    return value.field.description

QuestionLabel = widget.ComputedWidgetAttribute(
    getDescriptionAsLabel, view=IQuestionnaireGroup)


class DataColumn(column.SortingColumn):

    def __init__(self, field):
        super(DataColumn, self).__init__(field.title, field.__name__)

    def renderCell(self, item, formatter):
        return item.widgets[self.name].render()

    def getSortKey(self, item, formatter):
        return item.widgets[self.name].value


class QuestionnaireRow(form.DisplayForm):
    fields = field.Fields(interfaces.IQuestionnaire)


class QuestionnaireResults(browser.BrowserPagelet):
    zope.interface.implements(IQuestionnairePage)

    rowFields = field.Fields(interfaces.IQuestionnaire)

    def getContent(self):
        return [obj for obj in self.context.values()
                if interfaces.IQuestionnaire.providedBy(obj)]

    def update(self):
        super(QuestionnaireResults, self).update()

        rows = []
        for questionnaire in self.getContent():
            row = QuestionnaireRow(questionnaire, self.request)
            row.update()
            rows.append(row)

        columns = [DataColumn(field.field)
                   for field in self.rowFields.values()]

        self.table = formatter.ListFormatter(
            self.context, self.request, rows,
            prefix = 'formdemo.questionnaire.', columns=columns,
            sort_on=[('name', False)])
        self.table.widths = (160, 45, 65, 55, 65, 50, 70, 55, 100)
        for col in ('age', 'zope2', 'plone', 'zope3', 'five',
                    'contributor', 'years', 'zopeId'):
            self.table.columnCSS[col] = 'right'
        self.table.sortKey = 'formdemo.questionnaire.sort-on'

