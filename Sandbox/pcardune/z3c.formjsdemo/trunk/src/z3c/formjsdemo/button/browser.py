import zope.interface
from z3c.form import form, button
from z3c.formui import layout
from z3c.formjs import jsbutton, jsevent

class IButtons(zope.interface.Interface):
    show = jsbutton.JSButton(title=u'Show Code')
    hide = jsbutton.JSButton(title=u'Hide Code')

class ButtonForm(layout.FormLayoutSupport, form.EditForm):

    buttons = button.Buttons(IButtons)

    @jsevent.handler(IButtons['show'])
    def apply(self, id):
        return '$("#code").slideDown()'

    @jsevent.handler(IButtons['hide'])
    def apply(self, id):
        return '$("#code").slideUp()'
