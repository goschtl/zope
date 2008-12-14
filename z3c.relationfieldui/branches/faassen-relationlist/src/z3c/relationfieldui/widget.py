import grokcore.component as grok
from xml.sax.saxutils import escape

from zope.app.form.interfaces import IInputWidget, IDisplayWidget
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.app.form.browser import TextWidget, DisplayWidget, SimpleInputWidget
from zope import component
from zope.component.interfaces import ComponentLookupError
from zope.app.form.browser.widget import renderElement
from zope.traversing.browser import absoluteURL

from z3c.objpath.interfaces import IObjectPath
from hurry.resource import Library, ResourceInclusion
from hurry.js.wforms import wforms

from z3c.relationfield.schema import IRelation, IRelationList
from z3c.relationfield.interfaces import IRelationInfo

relation_lib = Library('z3c.relationfieldui')
relation_resource = ResourceInclusion(relation_lib, 'relation.js')

class RelationWidget(grok.MultiAdapter, TextWidget):
    grok.adapts(IRelation, IBrowserRequest)
    grok.provides(IInputWidget)

    def __call__(self):
        result = TextWidget.__call__(self)
        explorer_url = component.getMultiAdapter((self.context.context,
                                                 self.request),
                                                 name="explorerurl")()
        result += renderElement(
            'input', type='button', value='get relation',
            onclick="Z3C.relation.popup(this.previousSibling, '%s')" %
            explorer_url)
        relation_resource.need()
        return result

    def _toFieldValue(self, input):
        if not input:
            return None
        # convert path to Relation object
        obj = self.resolve(input)
        # XXX if obj is none, cannot create path
        return IRelationInfo(obj).createRelation()

    def _toFormValue(self, value):
        if value is None:
            return ''
        return value.to_path

    def resolve(self, path):
        object_path = component.getUtility(IObjectPath)
        return object_path.resolve(path)


class RelationDisplayWidget(grok.MultiAdapter, DisplayWidget):
    grok.adapts(IRelation, IBrowserRequest)
    grok.provides(IDisplayWidget)

    def __call__(self):
        if self._renderedValueSet():
            value = self._data
        else:
            value = self.context.default
        if value == self.context.missing_value:
            return ""
        to_object = value.to_object
        try:
            to_url = component.getMultiAdapter((to_object, self.request),
                                               name="relationurl")()
        except ComponentLookupError:
            to_url = absoluteURL(to_object, self.request)
        return '<a href="%s">%s</a>' % (
            to_url,
            escape(value.to_path))

class RelationListWidget(grok.MultiAdapter, TextWidget):
    grok.adapts(IRelationList, IBrowserRequest)
    grok.provides(IInputWidget)

    def __call__(self):
        result = '<fieldset class="repeat" id="%s">' % self.name
#        result += '<div class="oneField">'
        result += TextWidget.__call__(self)
        explorer_url = component.getMultiAdapter((self.context.context,
                                                 self.request),
                                                 name="explorerurl")()
        result += renderElement(
            'input', type='button', value='get relation',
            onclick="Z3C.relation.popup(this.previousSibling, '%s')" %
            (explorer_url))
 #       result += '</div>'
        result += '</fieldset>'
        wforms.need()
        relation_resource.need()
        return result

    def hasInput(self):
        # in case of a single response
        if self.name in self.request.form:
            return True
        # if multiple responses are there
        return self.name + '[0]-RC' in self.request.form

    def repeatCount(self):
        count = self.request.form.get(self.name + '[0]-RC', None)
        if count is None:
            return None
        return int(count)
    
    def _toFieldValue(self, input):
        c = self.repeatCount()
        if c is None:
            # regular single value input
            if not input:
                return []
            paths = [input]
        else:
            # multi-value input
            paths = []
            for i in range(c):
                v = self.request.form.get(self.name + '[%s]' % i, None)
                if v is None:
                    continue
                paths.append(v)
        result = []
        object_path = component.getUtility(IObjectPath)
        resolve = object_path.resolve
        for path in paths:
            obj = resolve(path)
            result.append(IRelationInfo(obj).createRelation())
        return result
        
    def _toFormValue(self, value):
        if value is None:
            return ''
        return value.to_path
