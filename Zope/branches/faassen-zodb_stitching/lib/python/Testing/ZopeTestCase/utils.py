#
# Utility functions
#
# These functions are designed to be imported and run at
# module level to add functionality to the test environment.
#

# $Id: utils.py,v 1.21 2005/02/11 09:00:21 shh42 Exp $


def setupCoreSessions(app=None):
    '''Sets up the session_data_manager e.a.'''
    from Acquisition import aq_base
    commit = 0

    if app is None: 
        return appcall(setupCoreSessions)

    if not hasattr(app, 'temp_folder'):
        from Products.TemporaryFolder.TemporaryFolder import MountedTemporaryFolder
        tf = MountedTemporaryFolder('temp_folder','Temporary Folder')
        app._setObject('temp_folder', tf)
        commit = 1

    if not hasattr(aq_base(app.temp_folder), 'session_data'):
        from Products.Transience.Transience import TransientObjectContainer
        toc = TransientObjectContainer('session_data',
                    'Session Data Container',
                    timeout_mins=3,
                    limit=100)
        app.temp_folder._setObject('session_data', toc)
        commit = 1

    if not hasattr(app, 'browser_id_manager'):
        from Products.Sessions.BrowserIdManager import BrowserIdManager
        bid = BrowserIdManager('browser_id_manager',
                    'Browser Id Manager')
        app._setObject('browser_id_manager', bid)
        commit = 1

    if not hasattr(app, 'session_data_manager'):
        from Products.Sessions.SessionDataManager import SessionDataManager
        sdm = SessionDataManager('session_data_manager',
                    title='Session Data Manager',
                    path='/temp_folder/session_data',
                    requestName='SESSION')
        app._setObject('session_data_manager', sdm)
        commit = 1

    if commit: get_transaction().commit()


def setupZGlobals(app=None):
    '''Sets up the ZGlobals BTree required by ZClasses.'''
    if app is None: 
        return appcall(setupZGlobals)

    root = app._p_jar.root()
    if not root.has_key('ZGlobals'):
        from BTrees.OOBTree import OOBTree
        root['ZGlobals'] = OOBTree()
        get_transaction().commit()


def setupSiteErrorLog(app=None):
    '''Sets up the error_log object required by ZPublisher.'''
    if app is None: 
        return appcall(setupSiteErrorLog)

    if not hasattr(app, 'error_log'):
        try:
            from Products.SiteErrorLog.SiteErrorLog import SiteErrorLog
        except ImportError:
            pass
        else:
            app._setObject('error_log', SiteErrorLog())
            get_transaction().commit()


import os, time

def importObjectFromFile(container, filename, quiet=0):
    '''Imports an object from a (.zexp) file into the given container.'''
    from ZopeLite import _print
    start = time.time()
    if not quiet: _print("Importing %s ... " % os.path.basename(filename))
    container._importObjectFromFile(filename, verify=0)
    get_transaction().commit()
    if not quiet: _print('done (%.3fs)\n' % (time.time() - start))


_Z2HOST = None
_Z2PORT = None

def startZServer(number_of_threads=1, log=None):
    '''Starts an HTTP ZServer thread.'''
    global _Z2HOST, _Z2PORT
    if _Z2HOST is None:
        import random
        _Z2HOST = '127.0.0.1'
        _Z2PORT = random.choice(range(55000, 55500))
        from ZServer import setNumberOfThreads
        setNumberOfThreads(number_of_threads)
        from threadutils import QuietThread, zserverRunner
        t = QuietThread(target=zserverRunner, args=(_Z2HOST, _Z2PORT, log))
        t.setDaemon(1)
        t.start()
        time.sleep(0.1) # Sandor Palfy
    return _Z2HOST, _Z2PORT


import sys

def makerequest(app, stdout=sys.stdout):
    '''Wraps the app into a fresh REQUEST.'''
    from ZPublisher.BaseRequest import RequestContainer
    from ZPublisher.Request import Request
    from ZPublisher.Response import Response
    response = Response(stdout=stdout)
    environ = {}
    environ['SERVER_NAME'] = _Z2HOST or 'nohost'
    environ['SERVER_PORT'] = '%d' % (_Z2PORT or 80)
    environ['REQUEST_METHOD'] = 'GET'
    request = Request(sys.stdin, environ, response)
    request._steps = ['noobject'] # Fake a published object
    return app.__of__(RequestContainer(REQUEST=request))


def appcall(function, *args, **kw):
    '''Calls a function passing 'app' as first argument.'''
    from base import app, close
    app = app()
    args = (app,) + args
    try:
        return function(*args, **kw)
    finally:
        close(app)


def makelist(arg):
    '''Turns arg into a list. Where arg may be
       list, tuple, or string.
    '''
    if type(arg) == type([]):
        return arg
    if type(arg) == type(()):
        return list(arg)
    if type(arg) == type(''):
       return filter(None, [arg])
    raise ValueError('Argument must be list, tuple, or string')


class ConnectionRegistry:
    '''ZODB connection registry'''

    def __init__(self):
        self._conns = []

    def register(self, conn):
        self._conns.append(conn)

    def close(self, conn):
        try: self._conns.remove(conn)
        except: pass
        try: conn.close()
        except: pass

    def closeAll(self):
        for conn in self._conns:
            try: conn.close()
            except: pass
        self._conns = []

    def __len__(self):
        return len(self._conns)

    def contains(self, conn):
        return conn in self._conns


__all__ = [
    'setupCoreSessions',
    'setupSiteErrorLog',
    'setupZGlobals',
    'startZServer',
    'importObjectFromFile',
    'appcall',
]

