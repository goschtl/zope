
import zope.interface
import zope.component

from zope.app.generations.utility import findObjectsProviding
from zope.app.zopeappgenerations import getRootFolder

from zope.app.file.interfaces import IFile
import zope.app.file
from ZODB.blob import Blob
import z3c.blobfile.file
import z3c.blobfile.image


def evolveZopeAppFile(root):
    """Replaces the classes and data of zope.app.file objects.
    
    Leaves annotations, key references, int id etc. intact.
    Doesn't throw an ObjectModify event.
    """
    for file in findObjectsProviding(root, IFile):
        data = file.data
        
        file._blob = Blob()
        
        if isinstance(file, zope.app.file.File):
            file.__class__ = z3c.blobfile.file.File
           
        if isinstance(file, zope.app.file.Image):
            file.__class__ = z3c.blobfile.image.Image    
            
        file.data = data    
         
    
def evolve(context):
    """
    Replaces all zope.app.file content objects with z3c.blobfile counterparts.
    """

    root = getRootFolder(context)

    evolveZopeAppFile(root)
