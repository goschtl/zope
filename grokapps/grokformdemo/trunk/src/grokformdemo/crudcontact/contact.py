import grok

from zope.interface import Interface
from zope.schema import TextLine
from grokformdemo.app import Grokformdemo
from megrok.z3cform.base import extends, button, PageAddForm, PageEditForm, PageDisplayForm, Fields
from megrok.z3cform.tabular import DeleteFormTablePage
from megrok.z3ctable import LinkColumn, NameColumn, GetAttrColumn, CheckBoxColumn


# Interface
class IContact(Interface):
    name = TextLine(title=u"Name")
    surname = TextLine(title=u"Surname")
    email = TextLine(title=u"Email")
    phone = TextLine(title=u"Phone")

# Content
class Contact(grok.Model):
    grok.implements(IContact)

    def __init__(self, name="", surname="", email="", phone=""):
        self.name = name 
        self.surname = surname 
        self.email = email 
        self.phone = phone 

# Container
class ContactContainer(grok.Container):
    pass


class ContainerIndex(DeleteFormTablePage):
    grok.name('index')
    grok.context(ContactContainer)
    extends(DeleteFormTablePage)
    status = None

    @button.buttonAndHandler(u'Add new Contact')
    def apply(self, action):
        self.redirect(self.url(self.context, 'add'))

    def executeDelete(self, object):
        del self.context[object.name]

    def render(self):
        return self.renderFormTable()

class CheckBox(CheckBoxColumn):
    grok.name('checkBox')
    grok.adapts(None, None, ContainerIndex)
    weight = 0

    def getItemKey(self, item):
        return '%s-selectedItems-%s' % (self.id, item.__name__)

class Name(LinkColumn):
    grok.name('Name')
    grok.adapts(None, None, ContainerIndex)
    weight = 1
    linkName = u"index"


class Surname(GetAttrColumn):
    grok.name('surname')
    grok.adapts(None, None, ContainerIndex)
    attrName = u"surname"
    weight = 2 


class Email(GetAttrColumn):
    grok.name('email')
    grok.adapts(None, None, ContainerIndex)
    attrName = u"email"
    weight = 3


class Phone(GetAttrColumn):
    grok.name('phone')
    grok.adapts(None, None, ContainerIndex)
    attrName = u"phone"
    weight = 4 

# Add A Default Conatiner
@grok.subscribe(Grokformdemo, grok.IObjectAddedEvent)
def addContactContainer(context, event):
    context['contacts'] = ContactContainer()


#Views
class Add(PageAddForm):
    grok.context(ContactContainer)
    fields = Fields(IContact)

    def create(self, data):
        return Contact(**data)

    def add(self, object):
        self.object = object
        self.context[object.name] = object
        return object

    def nextURL(self):
        return self.url(self.object)


class Edit(PageEditForm):
    grok.context(Contact)
    fields = Fields(IContact)


class Index(PageDisplayForm):
    grok.context(Contact)
    fields = Fields(IContact)
    actions = []
    #template = grok.PageTemplateFile('display.pt')

