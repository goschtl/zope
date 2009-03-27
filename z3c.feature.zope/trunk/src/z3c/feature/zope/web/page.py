import zope.schema
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

from z3c.form.form import EditForm
from z3c.form.field import Fields
from z3c.form.browser.textlines import TextLinesFieldWidget
from z3c.feature.zope.browser import ZopePageFeature
from z3c.feature.zope import interfaces

class ZopePageWebView(EditForm):
    label = u'Zope Page'
    fields = Fields(interfaces.IZopePageFeature)


class ZopePageWebFeature(object):
    viewFactory = ZopePageWebView
    contentFactory = ZopePageFeature
    title = u"Zope Page"
    description = u"Adds a Zope Page."
