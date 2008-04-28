from zope import interface
from zope import component

from unittest import TestSuite, makeSuite, main, TestCase
from threading import Thread, currentThread

from zope.interface import implements
from zope.component import provideUtility, provideAdapter
from zope.testing.cleanup import CleanUp

from z3c.indexing.dispatch.interfaces import IDispatcher
from z3c.indexing.dispatch.interfaces import ITransactionalDispatcher
from z3c.indexing.dispatch.interfaces import IQueueReducer

from z3c.indexing.dispatch.queue import TransactionalDispatcher
from z3c.indexing.dispatch.queue import getDispatcher
from z3c.indexing.dispatch.constants import INDEX, REINDEX, UNINDEX
from z3c.indexing.dispatch.tests import utils

class QueueTests(CleanUp, TestCase):
    
    def setUp(self):
        self.dispatcher = TransactionalDispatcher()

    def tearDown(self):
        self.queues = {}
        self.dispatcher.clear()
        
    def _provide_dispatcher(self, name=""):
        factory = utils.MockDispatcherFactory()

        provideAdapter(
            factory,
            (IDispatcher, str),
            IDispatcher,
            name=name)

        return factory.queue
    
    def testInterface(self):
        self.failUnless(ITransactionalDispatcher.providedBy(self.dispatcher))

    def testQueueHook(self):
        class CaptainHook:
            def __init__(self):
                self.hooked = 0
            def __call__(self):
                self.hooked += 1
        hook = CaptainHook()
        dispatcher = self.dispatcher
        dispatcher.tmhook = hook
        self.assertEqual(hook.hooked, 0)
        dispatcher.index('foo')
        dispatcher.reindex('foo')
        dispatcher.reindex('bar')
        self.assertEqual(len(dispatcher.getState()), 3)
        self.assertEqual(hook.hooked, 3)
        dispatcher.commit()
        self.assertEqual(hook.hooked, 3)

    def testQueueState(self):
        dispatcher = self.dispatcher
        dispatcher.index('foo')
        self.assertEqual(dispatcher.getState(), [(INDEX, 'foo', None)])
        state = dispatcher.getState()
        dispatcher.reindex('bar')
        self.assertEqual(dispatcher.getState(), [(INDEX, 'foo', None), (REINDEX, 'bar', None)])
        dispatcher.setState(state)
        self.assertEqual(dispatcher.getState(), [(INDEX, 'foo', None)])
        dispatcher.commit()
        self.assertEqual(len(dispatcher), 0)

    def testDispatching(self):
        self.dispatcher.index('foo')
        queue = self._provide_dispatcher()
        self.dispatcher.commit()
        self.assertEqual(self.dispatcher.getState(), [])
        self.assertEqual(queue, [(INDEX, 'foo', None), 'flush'])

    def testMultipleDispatchers(self):
        dispatcher = self.dispatcher

        queue1 = self._provide_dispatcher(name='dispatcher1')
        queue2 = self._provide_dispatcher(name='dispatcher2')
        
        dispatcher.index('foo')
        dispatcher.commit()
        
        self.assertEqual(dispatcher.getState(), [])
        self.assertEqual(queue1, [(INDEX, 'foo', None), 'flush'])
        self.assertEqual(queue2, [(INDEX, 'foo', None), 'flush'])

    def testQueueOperations(self):
        dispatcher = self.dispatcher
        
        queue = self._provide_dispatcher()
        
        dispatcher.index('foo')
        dispatcher.reindex('foo')
        dispatcher.unindex('foo')

        dispatcher.commit()

        self.assertEqual(len(dispatcher), 0)
        self.assertEqual(queue, [(INDEX, 'foo', None), (REINDEX, 'foo', None), (UNINDEX, 'foo', None), 'flush'])

    def testFlush(self):
        queue = self._provide_dispatcher()
        
        self.dispatcher.index('foo')
        self.dispatcher.commit()
        
        self.failUnless('flush' in queue)

    def testQueueReducer(self):
        class MessyReducer(object):
            implements(IQueueReducer)
            def optimize(self, queue):
                return [ op for op in queue if not op[0] == UNINDEX ]
        dispatcher = self.dispatcher
        dispatcher.index('foo')
        dispatcher.reindex('foo')
        dispatcher.unindex('foo')
        dispatcher.index('foo', 'bar')
        dispatcher._optimize()
        self.assertEqual(dispatcher.getState(), [(INDEX, 'foo', None), (REINDEX, 'foo', None), (UNINDEX, 'foo', None), (INDEX, 'foo', 'bar')])
        provideUtility(MessyReducer())  # hook up the reducer
        dispatcher._optimize()                # and try again...
        self.assertEqual(dispatcher.getState(), [(INDEX, 'foo', None), (REINDEX, 'foo', None), (INDEX, 'foo', 'bar')])

class QueueThreadTests(TestCase):
    """ thread tests modeled after zope.thread doctests """

    def setUp(self):
        self.dispatcher = getDispatcher()

    def tearDown(self):
        self.dispatcher.clear()

    def testLocalQueues(self):
        me = self.dispatcher                    # get the queued indexer...
        other = []
        def runner():                   # and a callable for the thread to run...
            me.reindex('bar')
            other[:] = me.getState()
        thread = Thread(target=runner)  # another thread is created...
        thread.start()                  # and started...
        while thread.isAlive(): '...'   # wait until it's done...
        self.assertEqual(other, [(REINDEX, 'bar', None)])
        self.assertEqual(me.getState(), [])
        me.index('foo')                 # something happening on our side...
        self.assertEqual(other, [(REINDEX, 'bar', None)])
        self.assertEqual(me.getState(), [(INDEX, 'foo', None)])
        thread.join()                   # finally the threads are re-united...

    def testQueuesOnTwoThreads(self):
        me = self.dispatcher                    # get the queued indexer...
        first = []
        def runner1():                  # and callables for the first...
            me.index('foo')
            first[:] = me.getState()
        thread1 = Thread(target=runner1)
        second = []
        def runner2():                  # and second thread
            me.index('bar')
            second[:] = me.getState()
        thread2 = Thread(target=runner2)
        self.assertEqual(first,  [])    # clean table before we start...
        self.assertEqual(second, [])
        self.assertEqual(me.getState(), [])
        thread1.start()                 # do stuff here...
        self.assertEqual(first,  [(INDEX, 'foo', None)])
        self.assertEqual(second, [])
        self.assertEqual(me.getState(), [])
        thread2.start()                 # and there...
        self.assertEqual(first,  [(INDEX, 'foo', None)])
        self.assertEqual(second, [(INDEX, 'bar', None)])
        self.assertEqual(me.getState(), [])
        thread1.join()                  # re-unite with first thread and...
        me.unindex('f00')               # let something happening on our side
        self.assertEqual(first,  [(INDEX, 'foo', None)])
        self.assertEqual(second, [(INDEX, 'bar', None)])
        self.assertEqual(me.getState(), [(UNINDEX, 'f00', None)])
        thread2.join()                  # also re-unite the second and...
        me.unindex('f00')               # let something happening again...
        self.assertEqual(first,  [(INDEX, 'foo', None)])
        self.assertEqual(second, [(INDEX, 'bar', None)])
        self.assertEqual(me.getState(), [(UNINDEX, 'f00', None), (UNINDEX, 'f00', None)])

    def testManyThreads(self):
        me = self.dispatcher                  # get the queued indexer...
        queues = {}                     # container for local queues
        def makeRunner(name, idx):
            def runner():
                for n in range(idx):    # index idx times
                    me.index(name)
                queues[currentThread()] = me.queue
            return runner
        threads = []
        for idx in range(99):
            threads.append(Thread(target=makeRunner('t%d' % idx, idx)))
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        for idx, thread in enumerate(threads):
            tid = 't%d' % idx
            queue = queues[thread]
            names = [ name for op, name, attrs in queue ]
            self.assertEquals(names, [tid] * idx)


def test_suite():
    return TestSuite([
        makeSuite(QueueTests),
        makeSuite(QueueThreadTests),
    ])

if __name__ == '__main__':
    main(defaultTest='test_suite')
