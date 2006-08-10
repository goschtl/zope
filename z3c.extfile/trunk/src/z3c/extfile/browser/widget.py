from zope.app.form.browser.textwidgets import FileWidget
from z3c.extfile import hashdir

class ExtBytesWidget(FileWidget):

    def _toFieldValue(self, si):
        # we pass the file object to the field
        return si
