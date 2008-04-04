import threading
import time
import signal
import transaction
import twisted.internet.selectreactor
import zope.component
import zope.app.appsetup.interfaces
import zc.twist

import zc.async.interfaces
import zc.async.queue
import zc.async.agent
import zc.async.dispatcher
import zc.async.utils

class QueueInstaller(object):

    def __init__(self, queues=('',),
                 factory=lambda *args: zc.async.queue.Queue(),
                 db_name=None):
        zope.component.adapter(
            zope.app.appsetup.interfaces.IDatabaseOpenedEvent)(self)
        self.db_name = db_name
        self.factory = factory
        self.queues = queues

    def __call__(self, ev):
        db = ev.database
        tm = transaction.TransactionManager()
        conn = db.open(transaction_manager=tm)
        tm.begin()
        try:
            try:
                root = conn.root()
                if zc.async.interfaces.KEY not in root:
                    if self.db_name is not None:
                        other = conn.get_connection(self.db_name)
                        queues = other.root()[
                            zc.async.interfaces.KEY] = zc.async.queue.Queues()
                        other.add(queues)
                    else:
                        queues = zc.async.queue.Queues()
                    root[zc.async.interfaces.KEY] = queues
                    tm.commit()
                    zc.async.utils.log.info('queues collection added')
                else:
                    queues = root[zc.async.interfaces.KEY]
                for queue_name in self.queues:
                    if queue_name not in queues:
                        queues[queue_name] = self.factory(conn, queue_name)
                        tm.commit()
                        zc.async.utils.log.info('queue %r added', queue_name)
            except:
                tm.abort()
                raise
        finally:
            conn.close()

queue_installer = QueueInstaller()

@zope.component.adapter(zope.app.appsetup.interfaces.IDatabaseOpenedEvent)
def installThreadedDispatcher(ev):
    reactor = twisted.internet.selectreactor.SelectReactor()
    # reactor._handleSignals()
    curr_sigint_handler = signal.getsignal(signal.SIGINT)
    def sigint_handler(*args):
        reactor.callFromThread(reactor.stop)
        time.sleep(0.5) # bah, a guess, but Works For Me (So Far)
        curr_sigint_handler(*args)
    def handler(*args):
        reactor.callFromThread(reactor.stop)
    signal.signal(signal.SIGINT, sigint_handler)
    signal.signal(signal.SIGTERM, handler)
    # Catch Ctrl-Break in windows
    if getattr(signal, "SIGBREAK", None) is not None:
        signal.signal(signal.SIGBREAK, handler)
    dispatcher = zc.async.dispatcher.Dispatcher(ev.database, reactor)
    def start():
        dispatcher.activate()
        reactor.run(installSignalHandlers=0)
    thread = threading.Thread(target=start)
    thread.setDaemon(True)
    thread.start()

class AgentInstaller(object):

    def __init__(self, agent_name='', chooser=None, size=3, queue_names=None):
        zope.component.adapter(
            zc.async.interfaces.IDispatcherActivated)(self)
        self.queue_names = queue_names
        self.agent_name = agent_name
        self.chooser = chooser
        self.size = size

    def __call__(self, ev):
        dispatcher = ev.object
        if (self.queue_names is None or
            dispatcher.parent.name in self.queue_names):
            if self.agent_name not in dispatcher:
                dispatcher[self.agent_name] = zc.async.agent.Agent(
                    chooser=self.chooser, size=self.size)
                zc.async.utils.log.info(
                    'agent %r added to queue %r',
                    self.agent_name,
                    dispatcher.parent.name)
            else:
                zc.async.utils.log.info(
                    'agent %r already in queue %r',
                    self.agent_name,
                    dispatcher.parent.name)

agent_installer = AgentInstaller('main')