from zope.app.form.browser import ListSequenceWidget
from zope.app.form.interfaces import IInputWidget
from zope.app.form.browser.widget import renderElement
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

from zope import component

from hurry.resource import Library, ResourceInclusion

listjs_lib = Library('z3c.listjs')
listjs_resource = ResourceInclusion(listjs_lib, 'listjs.js')

class _ListJsWidget(ListSequenceWidget):

    template = ViewPageTemplateFile('listjswidget.pt')
    record_template = ViewPageTemplateFile('listjswidget_record.pt')

    def widgetTemplate(self):
        # XXX hack: always get a widget that isn't in the sequence
        sequence = self._getRenderedValue()
        return self._getWidget(len(sequence))()
    
    def __call__(self):
        result = ListSequenceWidget.__call__(self)
        listjs_resource.need()
        return result
    
    def _getPresenceMarker(self, count=0):
        return ('<input type="hidden" id="%s.count" name="%s.count" value="%d" />'
                % (self.name, self.name, count))


def ListJsWidget(field, request):
    return _ListJsWidget(field, field, request)

