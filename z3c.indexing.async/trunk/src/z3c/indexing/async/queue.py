import Queue, threading

# we do async indexing with all indexing operations put into this queue
index_queue = Queue.Queue()

# async queue processor
class QueueProcessor( object ):

    # Flush every _n_ changes to the db
    FLUSH_THRESHOLD = 20

    # Flush every _n_ seconds since the last change
    FLUSH_TIMEOUT = 60

    indexer_running = False
    indexer_thread = None

    def __iter__(self):
        # iterator never ends, just sleeps when no results to process
        while self.indexer_running:
            # get an operation in blocking fashion
            try:
                op = index_queue.get(True, self.FLUSH_TIMEOUT)
            except Queue.Empty:
                yield None
            else:
                yield op

    def __call__(self):
        # number of documents indexed since last flush
        op_delta = 0
        
        dispatchers = set()

        def flush():
            for dispatcher in dispatchers:
                dispatcher.flush()

            dispatchers.clear()
            
        # loop through queue iteration
        for process in self:

            # on timeout the op is none
            if process is None:
                # if we indexed anything since the last flush, flush it now
                if op_delta:
                    flush()
                    op_delta = 0
                continue

            # process the operation
            process.dispatch()

            # keep track of dispatcher
            dispatchers.add(process.dispatcher)
            
            op_delta += 1
            
            if op_delta % self.FLUSH_THRESHOLD == 0:
                flush()
                op_delta = 0

    @classmethod
    def start(klass):
        if klass.indexer_running:
            raise SyntaxError("Indexer already running")
        
        klass.indexer_running = True
        indexer = klass()
        klass.indexer_thread = threading.Thread(target=indexer)
        klass.indexer_thread.setDaemon(True)
        klass.indexer_thread.start()
        return indexer

    @classmethod
    def stop(klass):
        if not klass.indexer_running:
            return
        klass.indexer_running = False
        klass.indexer_thread.join()
