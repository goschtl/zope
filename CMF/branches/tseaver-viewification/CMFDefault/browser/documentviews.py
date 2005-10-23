from Products.CMFDefault.exceptions import EditingConflict
from Products.CMFDefault.exceptions import IllegalHTML
from Products.CMFDefault.exceptions import ResourceLockedError
from Products.CMFDefault.utils import MessageID as _
from Products.CMFDefault.utils import scrubHTML

from utils import FormViewBase


class DocumentEditView(FormViewBase):

    """ Edit view for IMutableDocument.
    """

    # XXX: _BUTTONS this should become configurable
    _BUTTONS = ({'name': 'change',
                 'value': _('Change'),
                 'transform': ('validateTextFile', 'validateHTML', 'update'),
                 'redirect': ('context', 'object/edit')},
                {'name': 'change_and_view',
                 'value': _('Change and View'),
                 'transform': ('validateTextFile', 'validateHTML', 'update'),
                 'redirect': ('context', 'object/view')})

    def validateTextFile(self, file='', **kw):
        try:
            upload = file.read()
        except AttributeError:
            return self.setStatus(True)
        else:
            if upload:
                return self.setStatus(True, text=upload)
            else:
                return self.setStatus(True)

    def validateHTML(self, text, description='', **kw):
        try:
            description = scrubHTML(description)
            text = scrubHTML(text)
            return self.setStatus(True, text=text, description=description)
        except IllegalHTML, errmsg:
            return self.setStatus(False, errmsg)

    def update(self, text_format, text, SafetyBelt='', **kw):
        context = self.context
        if text_format != context.text_format or text != context.text:
            try:
                context.edit(text_format, text, safety_belt=SafetyBelt)
                return self.setStatus(True, _('Document changed.'))
            except (ResourceLockedError, EditingConflict), errmsg:
                return self.setStatus(False, errmsg)
        else:
            return self.setStatus(False, _('Nothing to change.'))
