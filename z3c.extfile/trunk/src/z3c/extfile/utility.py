from zope import component
import os
import hashdir
import interfaces

def bootStrapSubscriber(event):
    """create an IHashDir util if the EXTFILE_STORAGEDIR environment
    variable is present"""

    if os.environ.has_key('EXTFILE_STORAGEDIR'):
        path = os.environ.get('EXTFILE_STORAGEDIR')
        if not os.path.exists(path):
            raise ValueError, path
        hd = hashdir.HashDir(path)
        component.provideUtility(hd, provides=interfaces.IHashDir)


