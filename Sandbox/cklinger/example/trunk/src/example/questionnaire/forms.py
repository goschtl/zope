import grok
import zope.interface
from z3c.form import button, field, form, group, widget
import interfaces
import  questionnaire
import megrok.z3cform 
from example.app import Example, MySkin


##table
from zc.table import column
from zope.traversing.browser import absoluteURL
import formatter

grok.layer(MySkin)

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



class QuestionnaireAddForm( group.GroupForm, megrok.z3cform.AddForm ):
    #grok.name('quadd')
    grok.context(Example)
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
        return url + '/quResults'


class DataColumn(column.SortingColumn):

    def __init__(self, field):
        super(DataColumn, self).__init__(field.title, field.__name__)

    def renderCell(self, item, formatter):
        return item.widgets[self.name].render()

    def getSortKey(self, item, formatter):
        return item.widgets[self.name].value


class QuestionnaireRow(form.DisplayForm):
    fields = field.Fields(interfaces.IQuestionnaire)



class QuestionnaireResults(megrok.pagelet.Pagelet):
    grok.context(Example)
    grok.name('quResults')
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


#    def render(self):
#	return """
#	<h1>Zope Developer Questionnaire Results</h1>
#
#	<div tal:replace="structure view/table" />
#         <span tal:content="view"/> FUCKing heLL
#	<div class="actions">
#	  <a href="questionnaireaddform">[Fill out Questionnaire]</a>
#	  </div>
#	  """

