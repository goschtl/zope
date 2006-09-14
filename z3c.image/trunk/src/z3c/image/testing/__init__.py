#testing package
import os
from zope.app.file.image import Image

dataDir = os.path.join(os.path.dirname(__file__),'data')

def getTestImage(name):
    """returns a zope image with the given name from this directory"""
    path = os.path.join(dataDir,name)
    return Image(file(path, 'rb').read())
