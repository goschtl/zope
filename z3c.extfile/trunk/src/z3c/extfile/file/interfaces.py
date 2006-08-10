from z3c.extfile.schema import ExtBytesField
from zope.app.file.interfaces import IFile

class IExtFile(IFile):

    data = ExtBytesField(title=u'Data')
