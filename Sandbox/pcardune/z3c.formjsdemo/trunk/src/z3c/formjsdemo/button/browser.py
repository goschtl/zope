import os.path
import zope.interface
from z3c.form import form, button, field
from z3c.formui import layout
from z3c.formjs import jsbutton, jsevent

class IButtons(zope.interface.Interface):
    show = jsbutton.JSButton(title=u'Show JavaScript')
    hide = jsbutton.JSButton(title=u'Hide JavaScript')

class IFields(zope.interface.Interface):
    file = zope.schema.Choice(
        title=u"File",
        description=u"The file to show.",
        required=True,
        default=u"None",
        values=(u"None",u"browser.py",u"button.pt",u"configure.zcml")
        )

class ButtonForm(layout.FormLayoutSupport, form.EditForm):

    buttons = button.Buttons(IButtons)
    fields = field.Fields(IFields)

    @jsevent.handler(buttons['show'])
    def apply(self, id):
        return '$("#javascript").slideDown()'

    @jsevent.handler(buttons['hide'])
    def apply(self, id):
        return '$("#javascript").slideUp()'

    @jsevent.handler(fields['file'], event=jsevent.CHANGE)
    def handleFileChange(self, id):
        return '''
            $(".code").hide();
            $("#"+$("#%s").val().replace(".","-")).show();''' % id

    def getFile(self, filename):
        here = os.path.dirname(os.path.abspath(__file__))
        f = open(os.path.join(here, filename), 'r')
        data = f.read()
        f.close()
        return data
