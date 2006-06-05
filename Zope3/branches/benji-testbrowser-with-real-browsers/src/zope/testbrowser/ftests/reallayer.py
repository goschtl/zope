from zope.app.server.main import setup, load_options, run
import ThreadedAsync.LoopCallback
import threading
from zope.testbrowser.realproxy import TARGET_PORT

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
        def go():
            # force the server to run on a known port
            args = ['-X', 'server/address=%s' % TARGET_PORT,
                    '-X', 'site-definition=ftesting.zcml']
            setup(load_options(args))
            run()

        self.zope_thread = threading.Thread(target=go)
        self.zope_thread.setDaemon(True)
        self.zope_thread.start()

    def stopZope(self):
        """tell Zope to stop and wait for it to do so"""
        ThreadedAsync.LoopCallback.exit_status = 0
        self.zope_thread.join()

TestbrowserReal = TestbrowserRealClass()
