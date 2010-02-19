import grok

from zope.interface import Interface
from grok.interfaces import IApplication
from megrok.reload.code import reload_code
from megrok.reload.zcml import reload_zcml
from megrok.reload.interfaces import IReload
from zope.schema.interfaces import IVocabularyFactory
from zope.component import getAllUtilitiesRegisteredFor
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from grokcore.component.testing import grok as grok_module

from widgets import MultiCheckBoxWidget

def null_validator(*args, **kwargs):
    """A validator that doesn't validate anything.
    
    This is somewhat lame, but if you have a "Cancel" type button that
    won't want to validate the form, you need something like this.

    @form.action(_(u"label_cancel", default=u"Cancel"),
                 validator=null_validator,
                 name=u'cancel')
    """
    return ()


class ApplicationVocabulary(grok.GlobalUtility):
    grok.implements(IVocabularyFactory)
    grok.name(u'megrok.reload.applications')

    def __call__(self, context):
        rc = []
        apps = getAllUtilitiesRegisteredFor(IApplication)
        for app in apps:
            rc.append(SimpleTerm(app.__module__, app.__name__, app.__name__))
        return SimpleVocabulary(rc)

class MultiCheckBoxVocabularyWidget(MultiCheckBoxWidget):
    """ """

    def __init__(self, field, request):
        """Initialize the widget."""
        super(MultiCheckBoxVocabularyWidget, self).__init__(field,
            field.value_type.vocabulary, request)


class Reload(grok.Form):
    """Reload view.
    """
    grok.context(Interface)
    grok.implements(IReload)
    message = None

    form_fields = grok.Fields(IReload)
    form_fields['applications'].custom_widget = MultiCheckBoxVocabularyWidget


    @grok.action(u'Reload Code', validator=null_validator)
    def handle_relaod(self, **kw):
        self.code_reload()

    @grok.action(u'Reload Code and ZCML')
    def handle_relaod(self, **kw):
        self.zcml_reload(kw.get('applications', []))

    def status(self):
        return self.message

    def code_reload(self):
        reloaded = reload_code()

        result = ''
        if reloaded:
            result += 'Code reloaded:\n\n'
            result += '\n'.join(reloaded)
        else:
            result = 'No code reloaded!'
        return result

    def zcml_reload(self, applications):
        reloaded = reload_code()
        for application in applications:
            grok_module(application.split('.')[0]) ### BBB: THIS IS VERY BUGGY...

        result = ''
        if reloaded:
            result += 'Code reloaded:\n\n'
            result += '\n'.join(reloaded)
        else:
            result = 'No code reloaded!'
        result += '\n\nGlobal ZCML reloaded.'
        return result
