import zope.interface
import zope.component
from z3c.form.interfaces import IWidget, IField

from jquery.layer import IJQueryJavaScriptBrowserLayer

from z3c.formjs import interfaces


## @zope.component.adapter(IWidget, IJQueryJavaScriptBrowserLayer)
## @zope.interface.implementer(interfaces.IJSErrorMessageRenderer)
## def JQueryErrorMessageRenderer(widgetID):
##     return '''$.get()'''


class JQueryBaseValidationRenderer(object):

    def __init__(self, form, field, request):
        self.form = form
        self.field = field # z3c.form.field.Field instance!!!
        self.request = request

    def _ajaxURL(self):
        widget = self.form.widgets[self.field.__name__]

        # build js expression for extracting widget value
        # XXX: Maybe we should adapt the widget to IJSValueExtractorRenderer?
        valueString = '$("#%s").val()' % (widget.id, )

        # build a js expression that joins valueString expression
        queryString = '"?widget-id=%s&value=" + %s' % (widget.id, valueString)

        # build a js expression that joins form url, validate path, and query string
        ajaxURL = '"'+self.form.request.getURL() + '/validate" + ' + queryString

        # it should look something like this now:
        # "path/to/form.html/validate" + "?widget-id=some-id&value=" + $("#some-id").val()
        return ajaxURL


class JQueryMessageValidationRenderer(JQueryBaseValidationRenderer):

    zope.interface.implements(interfaces.IJSMessageValidationRenderer)
    zope.component.adapts(interfaces.IAJAXValidator,
                          IField,
                          IJQueryJavaScriptBrowserLayer)

    def render(self):
        ajaxURL = self._ajaxURL()
        # build a js expression that shows the user the error message
        # XXX: later this should query for a renderer based on the widget
        #     jsrenderer = zope.component.queryMultiAdapter(
        #         (widget, self.request), interfaces.IJSErrorMessageRenderer)
        #     messageSetter = jsrenderer.render()
        messageSetter = 'alert(data);'
        ajax = '$.get(%s,\nfunction(data){\n%s\n})' % (ajaxURL, messageSetter)
        return ajax


class MessageValidationRenderer(object):
    """An intermediate class that performs adapter look ups.

    This way you don't have to do as many adapter look ups in your Form class.
    """

    def __init__(self, form, field):
        self.form = form
        self.field = field

    def render(self):
        jsrenderer = zope.component.queryMultiAdapter(
            (self.form, self.field, self.form.request), interfaces.IJSMessageValidationRenderer)
        return jsrenderer.render()


class BaseValidator(object):
    zope.interface.implements(interfaces.IAJAXValidator)

    ValidationRenderer = None

    def _validate(self):
        widgetID = self.request.get('widget-id')
        self.fields = self.fields.select(widgetID)
        self.updateWidgets()
        return self.widgets.extract()


class MessageValidator(BaseValidator):
    '''Validator that sends error messages for widget in questiodn.'''
    ValidationRenderer = MessageValidationRenderer

    def validate(self):
        data, errors = self._validate()
        if errors:
            return errors[0].doc()
        return u'' # all OK

