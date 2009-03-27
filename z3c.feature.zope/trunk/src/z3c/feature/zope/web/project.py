import zope.schema
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

from z3c.form.form import EditForm
from z3c.form.field import Fields
from z3c.form.browser.textlines import TextLinesFieldWidget
from z3c.feature.zope.project import ZopeProjectFeature
from z3c.feature.zope import interfaces

class ZopeProjectWebView(EditForm):
    label = u'Zope Project'
    fields = Fields(interfaces.IZopeProjectFeature)


class ZopeProjectWebFeature(object):
    viewFactory = ZopeProjectWebView
    contentFactory = ZopeProjectFeature
    title = u"Zope Project"
    description = u"Adds a Zope Project."
