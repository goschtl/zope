import logging
import transaction

import zope.interface
import zope.component

from zope.app.generations.utility import findObjectsProviding
from zope.app.zopeappgenerations import getRootFolder

from zope.app.file.interfaces import IFile
import zope.app.file
from ZODB.blob import Blob
import z3c.blobfile.file
import z3c.blobfile.image


def changeImplementation(file, klass):
    file._blob = Blob()
    _data = file.__dict__['_data']
    del file.__dict__['_data']
    file.__class__ = klass
    fp = file.open('w')
    if isinstance(_data, zope.app.file.file.FileChunk):
        fp.write(_data._data)
        del _data._data
        _data = _data.next
    else:
        fp.write(_data)
    del _data
    fp.close()
            
    
def evolveZopeAppFile(root):
    """Replaces the classes and data of zope.app.file objects.
    
    Leaves annotations, key references, int id etc. intact.
    Doesn't throw an ObjectModify event.
    """
    for file in findObjectsProviding(root, IFile):
        if isinstance(file, zope.app.file.File):
            changeImplementation(file, z3c.blobfile.file.File)
        elif isinstance(file, zope.app.file.Image):
            changeImplementation(file, z3c.blobfile.image.Image)
        else:
            logging.getLogger('z3c.blobfile.generations').warn(
            'Unknown zope.app.file.interfaces.IFile implementation %s.%s' % (
                file.__class__.__module__,
                file.__class__.__name__))
         
        transaction.savepoint(optimistic=True)
        
def evolve(context):
    """
    Replaces all zope.app.file content objects with z3c.blobfile counterparts.
    """

    root = getRootFolder(context)

    evolveZopeAppFile(root)
