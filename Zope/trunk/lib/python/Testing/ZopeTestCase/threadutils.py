#
# Parts of ZServer support are in this module so they can
# be imported more selectively.
#

# $Id: threadutils.py,v 1.6 2004/08/19 15:31:26 shh42 Exp $

from threading import Thread
from StringIO import StringIO

dummyLOG = StringIO()


def zserverRunner(host, port, log=None):
    '''Runs an HTTP ZServer on host:port.'''
    from ZServer import logger, asyncore
    from ZServer import zhttp_server, zhttp_handler
    if log is None: log = dummyLOG
    lg = logger.file_logger(log)
    hs = zhttp_server(ip=host, port=port, resolver=None, logger_object=lg)
    zh = zhttp_handler(module='Zope', uri_base='')
    hs.install_handler(zh)
    asyncore.loop()


class QuietThread(Thread):
    '''This thread eats all exceptions'''
    def __init__(self, target=None, args=(), kwargs={}):
        Thread.__init__(self, target=target, args=args, kwargs=kwargs)
        self.__old_bootstrap = Thread._Thread__bootstrap
    def __bootstrap(self):
        try: self.__old_bootstrap(self)
        except: pass
    _Thread__bootstrap = __bootstrap


def QuietPublisher(self, accept):
    '''This server eats all exceptions'''
    try: self.__old_init__(accept)
    except: pass


from ZServer.PubCore.ZServerPublisher import ZServerPublisher
if not hasattr(ZServerPublisher, '__old_init__'):
    ZServerPublisher.__old_init__ = ZServerPublisher.__init__
    ZServerPublisher.__init__ = QuietPublisher

