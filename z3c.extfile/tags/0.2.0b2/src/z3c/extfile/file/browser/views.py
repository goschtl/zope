from zope.formlib import form
from z3c.extfile.file.interfaces import IExtFile
from zope.i18nmessageid import MessageFactory
_ = MessageFactory("zope")
from zope.contenttype import guess_content_type

class EditForm(form.EditForm):
    form_fields = form.Fields(IExtFile)

    @form.action(_("Apply"), condition=form.haveInputWidgets)
    def handle_edit_action(self, action, data):
        #use the filename to guess the content type
        if not data.get('contentType'):
            try:
                filename = data.get('data').filename
            except:
                filename = None
            if filename:
                contentType = guess_content_type(filename)[0]
                if contentType:
                    data['contentType'] = contentType
        return super(EditForm, self).handle_edit_action.success(data)
        
        
