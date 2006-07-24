from zope.app.server.main import setup, load_options, run
from zope.testbrowser import realproxy
import ThreadedAsync.LoopCallback
import os
import tempfile
import threading

CONF = """\
site-definition %(SITE_ZCML)s

<server http>
  type HTTP
  address 127.0.0.1:%(TARGET_PORT)s
</server>

<zodb>
  <demostorage>
  </demostorage>
</zodb>

<accesslog>
</accesslog>

<eventlog>
</eventlog>
"""


class TestbrowserRealClass:

    __bases__ = ()

    def __init__(self):
        self.__name__ = self.__class__.__name__[:-5]
        self.__module__ = self.__class__.__module__

    def setUp(self):
        self.startZope()

    def tearDown(self):
        self.stopZope()

    def startZope(self, fg=None):
        """start Zope in a daemon thread"""
        SITE_ZCML = 'ftesting.zcml'
        TARGET_PORT = realproxy.TARGET_PORT
        handle, self.conf_path = tempfile.mkstemp()
        os.write(handle, CONF % locals())
        os.close(handle)

        def go():
            # force the server to run with a known config
            args = ['-C', self.conf_path]
            setup(load_options(args))
            run(timeout=1.0)

        self.zope_thread = threading.Thread(target=go)
        self.zope_thread.setDaemon(True)
        self.zope_thread.start()

    def stopZope(self):
        """tell Zope to stop and wait for it to do so"""
        import time; time.sleep(1) # XXX work around race condition
        ThreadedAsync.LoopCallback.exit_status = 0
        self.zope_thread.join()
        os.remove(self.conf_path)

TestbrowserReal = TestbrowserRealClass()
