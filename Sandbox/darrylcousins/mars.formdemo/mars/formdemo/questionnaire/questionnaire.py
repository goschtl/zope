__docformat__ = "reStructuredText"
import zope.interface
import zope.schema
from zope.schema import fieldproperty
from zope.traversing.browser import absoluteURL
from zope.app.folder.interfaces import IFolder
from zope.viewlet.viewlet import CSSViewlet

from z3c.form import button, field, form, group, widget
from z3c.form.interfaces import IAddForm
from z3c.formdemo.questionnaire.interfaces import IQuestionnaire
from z3c.formdemo.questionnaire.browser import (IQuestionnaireGroup,
                                                IQuestionnairePage,
                                                DevelopmentExperienceGroup,
                                                ContributorExperienceGroup,
                                                DataColumn,
                                                QuestionnaireRow)
from z3c.formdemo.browser import formatter
from z3c.formui import layout

from zc.table import column

import grok

import mars.form
import mars.view
import mars.template
import mars.layer
import mars.adapter
import mars.resource
from mars.formdemo.layer import IDemoBrowserLayer
from mars.formdemo.skin import skin

mars.layer.layer(IDemoBrowserLayer)


class Questionnaire(grok.Model):
    zope.interface.implements(IQuestionnaire)

    name = fieldproperty.FieldProperty(IQuestionnaire['name'])
    age = fieldproperty.FieldProperty(IQuestionnaire['age'])
    zope2 = fieldproperty.FieldProperty(IQuestionnaire['zope2'])
    plone = fieldproperty.FieldProperty(IQuestionnaire['plone'])
    zope3 = fieldproperty.FieldProperty(IQuestionnaire['zope3'])
    five = fieldproperty.FieldProperty(IQuestionnaire['five'])
    contributor = fieldproperty.FieldProperty(IQuestionnaire['contributor'])
    years = fieldproperty.FieldProperty(IQuestionnaire['years'])
    zopeId = fieldproperty.FieldProperty(IQuestionnaire['zopeId'])

    def __init__(self, **kw):
        for name, value in kw.items():
            setattr(self, name, value)


class QuestionnaireAddForm(mars.form.FormView, layout.AddFormLayoutSupport,
                          group.GroupForm, form.AddForm):
    """Questionnaire add form"""
    grok.name('addQuestionnaire')
    grok.context(IFolder)
    zope.interface.implements(IQuestionnairePage)

    label = u'Zope Developer Questionnaire'
    fields = field.Fields(IQuestionnaire).select('name', 'age')
    groups = (DevelopmentExperienceGroup, ContributorExperienceGroup)

    def create(self, data):
        return Questionnaire(**data)

    def add(self, object):
        count = 0
        while 'questionnaire-%i' %count in self.context:
            count += 1;
        self._name = 'questionnaire-%i' %count
        self.context[self._name] = object
        return object

    def nextURL(self):
        url = absoluteURL(self.context, self.request)
        return url + '/questionnaireResults'


class QuestionnaireResults(mars.view.PageletView):
    """Questionnaire results tabular view"""
    grok.name('questionnaireResults')
    grok.context(IFolder)
    zope.interface.implements(IQuestionnairePage)

    rowFields = field.Fields(IQuestionnaire)

    def getContent(self):
        return [obj for obj in self.context.values()
                if IQuestionnaire.providedBy(obj)]

    def update(self):

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

class ResultsTemplate(mars.template.TemplateFactory):
    """Template for results view"""
    grok.context(QuestionnaireResults)
    grok.template('results.pt')

## CSS requirement
class QuestionnaireStyle(mars.resource.ResourceFactory):
    """File resource"""
    grok.name('questionnaire.css')
    mars.resource.file('questionnaire.css')

QuestionnaireCSSViewlet = CSSViewlet('questionnaire.css')
class FormQuestionnaireSSViewlet(mars.viewlet.SimpleViewlet, QuestionnaireCSSViewlet):
    """css viewlet"""
    grok.name('questionnaire.css')
    grok.context(zope.interface.Interface)
    mars.viewlet.view(IQuestionnairePage)
    mars.viewlet.manager(skin.CSSManager)


## Form labels
class SubmitLabel(mars.adapter.AdapterFactory):
    grok.name('title')
    mars.adapter.factory(button.StaticButtonActionAttribute(
        u'Submit Questionnaire', button=form.AddForm.buttons['add'],
        form=QuestionnaireAddForm))

def getDescriptionAsLabel(value):
    return value.field.description

class QuestionLabel(mars.adapter.AdapterFactory):
    grok.name('label')
    mars.adapter.factory(widget.ComputedWidgetAttribute(
        getDescriptionAsLabel, view=IQuestionnaireGroup))

