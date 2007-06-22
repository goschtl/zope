from zope.app.form.browser import DropdownWidget

class OptionStorageVocabularyWidget(DropdownWidget):

    def _getDefault(self):
        default = self.vocabulary.getDefaultKey()
        if not default:
            default = super(OptionStorageVocabularyWidget, self)._getDefault()
        return default
