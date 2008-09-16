from zope.interface import implements
from zope.schema import Field

from hurry.file.interfaces import IFile
from hurry.file.file import HurryFile

class File(Field):
    __doc__ = IFile.__doc__

    implements(IFile)
    
    _type = HurryFile
