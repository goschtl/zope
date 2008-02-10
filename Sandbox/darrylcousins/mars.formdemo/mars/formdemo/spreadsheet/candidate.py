import zope.interface
from zope.schema import fieldproperty
from zope.viewlet.viewlet import CSSViewlet
from zope.app.folder.interfaces import IFolder

from z3c.form import field
from z3c.formdemo.spreadsheet.content import ICandidate

import grok

import mars.layer
import mars.viewlet
import mars.template
from mars.formdemo.layer import IDemoBrowserLayer
from mars.formdemo.skin import skin
from mars.formdemo.spreadsheet.spreadsheet import Spreadsheet

mars.layer.layer(IDemoBrowserLayer)

class Candidate(grok.Model):
    zope.interface.implements(ICandidate)

    lastName = fieldproperty.FieldProperty(ICandidate['lastName'])
    firstName = fieldproperty.FieldProperty(ICandidate['firstName'])
    rating = fieldproperty.FieldProperty(ICandidate['rating'])

    def __init__(self, lastName, firstName, rating=None):
        self.lastName = lastName
        self.firstName = firstName
        self.rating = rating

class CandidateSpreadsheet(mars.view.PageletView, Spreadsheet):
    grok.name('spreadsheet')
    grok.context(IFolder)

    sessionKey = 'mars.formdemo.spreadsheet.candidate'
    rowFields = field.Fields(ICandidate)
    columnWidths = (200, 200, 150)

    def getContent(self):
        return [obj for obj in self.context.values()
                if ICandidate.providedBy(obj)]

class CandidateSpreadsheetTemplate(mars.template.TemplateFactory):
    grok.context(CandidateSpreadsheet)
    grok.template('spreadsheet.pt')

## CSS requirement
class SpreadsheetStyle(mars.resource.ResourceFactory):
    """File resource"""
    grok.name('spreadsheet.css')
    mars.resource.file('spreadsheet.css')

SpreadsheetCSS = CSSViewlet('spreadsheet.css')
class SpreadsheetCSSViewlet(mars.viewlet.SimpleViewlet, SpreadsheetCSS):
    """css viewlet"""
    weight = 1000
    grok.name('spreadsheet.css')
    grok.context(zope.interface.Interface)
    mars.viewlet.view(CandidateSpreadsheet)
    mars.viewlet.manager(skin.CSSManager)

