from zope import component
import os
import hashdir
import interfaces
from zope.app.appsetup.product import getProductConfiguration
import logging
log = logging.getLogger('z3c.extfile')

def getPath():

    """returns the path of the storage directory

    If not path is defined None is returned

    >>> del os.environ['EXTFILE_STORAGEDIR']
    >>> getPath() is None
    True

    If we have a evnironment variable it is returned. If the path does
    not exist a ValueError is raised.

    >>> os.environ['EXTFILE_STORAGEDIR'] = '/this/path/does/not/exist'
    >>> getPath()
    Traceback (most recent call last):
    ...
    ValueError: Extfile storage path does not exist:
    '/this/path/does/not/exist'
    >>> os.environ['EXTFILE_STORAGEDIR'] = os.path.dirname(__file__)
    >>> getPath()
    '.../z3c/extfile'

    If we have a product configuration this is used.

    >>> class Config(object):
    ...     mapping = {}
    ...     def getSectionName(self):
    ...         return 'z3c.extfile'
    >>> config = Config()
    >>> path  = os.path.join(os.path.dirname(__file__), 'browser')
    >>> config.mapping['storagedir'] = path
    >>> from zope.app.appsetup.product import setProductConfigurations
    >>> setProductConfigurations([config])
    >>> getPath() is path
    True
    """

    path = None
    config = getProductConfiguration('z3c.extfile')
    if config is not None:
        path = config.get('storagedir')
    path = path or os.environ.get('EXTFILE_STORAGEDIR')
    if path is None:
        return
    if not os.path.exists(path):
        raise ValueError, "Extfile storage path does not exist: %r" % path
    return path

def bootStrapSubscriber(event):
    """create an IHashDir util if the EXTFILE_STORAGEDIR environment
    variable is present
    """
    path = getPath()
    if path is not None:
        # look first if we have utility already
        hd = component.queryUtility(interfaces.IHashDir)
        if hd is not None:
            log.warn('Ignoring hashdir path %r using already'
                     ' registered IHashDir Utility at %r' % (
                path,hd.path))
            return
        hd = hashdir.HashDir(path)
        component.provideUtility(hd, provides=interfaces.IHashDir)
        log.info('Registered IHashDir utility with storagedir: %r' % path)


