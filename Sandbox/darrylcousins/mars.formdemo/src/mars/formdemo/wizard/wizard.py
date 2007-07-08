__docformat__ = "reStructuredText"

import zope.interface
from zope.viewlet.viewlet import CSSViewlet
from zope.app.folder.interfaces import IFolder
from zope.app.session.interfaces import ISession

from z3c.form import form, field, button
from z3c.formui import layout
from z3c.formdemo.wizard import interfaces, browser, content
from z3c.formdemo.wizard.wizard import Wizard


import grok

import mars.view
import mars.viewlet
import mars.layer
from mars.formdemo.layer import IDemoBrowserLayer
from mars.formdemo.skin import skin

mars.layer.layer(IDemoBrowserLayer)

class PersonWizard(mars.view.PageletView, Wizard):
    grok.name('wizard')
    grok.context(IFolder)
    form.extends(Wizard)

    title = u'Wizard Demo - Person Demographics'
    sessionKey = 'z3c.formdemo.wizard.person'

    steps = [
        ('personalInfo', browser.PersonalInfoStep),
        ('address', browser.AddressStep),
        ('father', browser.FatherStep),
        ('mother', browser.MotherStep),
        ('employer', browser.EmployerStep)]

    def finish(self):
        self.request.response.redirect('summary')

    def getContent(self):
        session = ISession(self.request)[self.sessionKey]
        obj = session.get('content')
        if obj is None:
            obj = session['content'] = content.Person()
        return obj

    @button.buttonAndHandler(
        u'Clear', condition=lambda form: form.isFirstStep(),
        provides=(interfaces.IBackButton,))
    def handleClear(self, action):
        session = ISession(self.request)[self.sessionKey]
        del session['content']
        self.request.response.redirect(
            self.request.getURL() + '?step=' + self.steps[0][0])

class PersonSummary(mars.view.FormView, layout.FormLayoutSupport, form.DisplayForm):
    grok.name('summary')
    grok.context(zope.interface.Interface)

    fields = field.Fields(interfaces.IPersonalInfo).select(*browser.infoSelection)

    def getContent(self):
        session = ISession(self.request)[PersonWizard.sessionKey]
        return session.get('content')

    def update(self):
        content = self.getContent()
        self.father = form.DisplayForm(content.father, self.request)
        self.father.fields = field.Fields(interfaces.IPersonalInfo).select(
            *browser.infoSelection)
        self.father.update()

        self.mother = form.DisplayForm(content.mother, self.request)
        self.mother.fields = field.Fields(interfaces.IPersonalInfo).select(
            *browser.infoSelection)
        self.mother.update()

        self.employer = form.DisplayForm(content.employer, self.request)
        self.employer.fields = field.Fields(interfaces.IEmployerInfo).select(
            'name', 'street', 'city', 'zip')
        self.employer.update()

        super(PersonSummary, self).update()

class PersonSummaryTemplate(mars.template.TemplateFactory):
    grok.context(PersonSummary)
    grok.template('summary.pt')


class WizardImages(mars.resource.ResourceDirectoryFactory):
    """image resource directory (++resource++img)"""
    grok.name('WizardImages')
    mars.resource.directory('images')


## CSS requirement
class WizardStyle(mars.resource.ResourceFactory):
    """File resource"""
    grok.name('wizard.css')
    mars.resource.file('wizard.css')

WizardCSS= CSSViewlet('wizard.css')
class WizardCSSViewlet(mars.viewlet.SimpleViewlet, WizardCSS):
    """css viewlet"""
    grok.name('wizard.css')
    grok.context(zope.interface.Interface)
    mars.viewlet.view(Wizard)
    mars.viewlet.manager(skin.CSSManager)

class WizardTemplate(mars.template.TemplateFactory):
    grok.context(Wizard)
    grok.template('wizard.pt')

class StepTemplate(mars.template.TemplateFactory):
    grok.context(interfaces.IStep)
    grok.template('step.pt')

