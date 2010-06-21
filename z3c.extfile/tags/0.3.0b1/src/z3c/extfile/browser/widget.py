from zope.app.form.browser.textwidgets import FileWidget

class ExtBytesWidget(FileWidget):

    def _toFieldValue(self, si):
        # we pass the file object to the field
        return si
