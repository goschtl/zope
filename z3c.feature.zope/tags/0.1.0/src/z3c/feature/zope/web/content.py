import zope.schema
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

from z3c.form.form import EditForm
from z3c.form.field import Fields
from z3c.form.browser.textlines import TextLinesFieldWidget
from z3c.feature.zope.content import ZopeContentFeature
from z3c.feature.zope import interfaces

class ZopeContentWebView(EditForm):
    label = u'Zope Content'
    fields = Fields(interfaces.IZopeContentFeature).select('className','classFile')


class ZopeContentWebFeature(object):
    viewFactory = ZopeContentWebView
    contentFactory = ZopeContentFeature
    title = u"Zope Content"
    description = (u"Adds a Content Type to zope with forms for adding, "
                   u"viewing, and editing the content.")
