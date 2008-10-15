#testing package
import os
from zope.app.file.image import Image

dataDir = os.path.join(os.path.dirname(__file__),'data')

def readTestImage(name):
    path = os.path.join(dataDir,name)
    return file(path, 'rb').read()

def getTestImage(name):
    """returns a zope image with the given name from this directory"""
    return Image(readTestImage(name))

