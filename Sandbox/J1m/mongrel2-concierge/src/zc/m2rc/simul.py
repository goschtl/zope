from marshal import dumps, loads

import bisect
import marshal
import logging
import multiprocessing
import optparse
import os
import random
import pylru
import time
import threading
import traceback
import sys
import zmq

mongrel2_pushreq_addr = 'tcp://127.0.0.1:9901'
mongrel2_subresp_addr = 'tcp://127.0.0.1:9902'
broker_apply_addr     = 'tcp://127.0.0.1:9903'

logging.basicConfig(level=logging.INFO, format='%(message)s')

log_level = logging.INFO

def log(*args):
    logging.log(log_level, ' '.join(map(str, args)))

def mongrel2(nsites=400, noids=10000, nout=1000, minsize=100, maxsize=2000,
             max_requests=100000, show_responses=True):
    log('mongrel2 pid=%s' % os.getpid())
    context = zmq.Context()
    push = context.socket(zmq.PUSH)
    push.bind(mongrel2_pushreq_addr)
    sub = context.socket(zmq.SUB)
    sub.bind(mongrel2_subresp_addr)
    sub.setsockopt(zmq.SUBSCRIBE, '')

    poller = zmq.Poller()
    poller.register(sub, zmq.POLLIN)

    oids = range(noids)
    sites = range(nsites)

    # grossly model unequal site sizes.
    sites = sites[:100] + sites
    sites = sites[:50] + sites
    sites = sites[:20] + sites
    sites = sites[:10]*2 + sites
    sites = sites[:5]*3 + sites

    nreq = 0
    outstanding = {}
    while 1:

        if nreq >= max_requests and not outstanding:
            break

        while nreq < max_requests and len(outstanding) < nout:
            site = random.choice(sites)
            size = random.randint(minsize, maxsize)
            work = random.sample(oids, size)
            nreq += 1
            outstanding[nreq] = sum(work), time.time()
            work[0:0] = site, nreq
            #log('request', nreq, sum(work[2:]), site, size)
            push.send(dumps(work, 1))

        ready = dict(poller.poll())
        if ready.get(sub) == zmq.POLLIN:
            mess = loads(sub.recv())
            if isinstance(mess, str):
                exec mess
                continue

            rreq, result, wtime, n, nhit, nmiss, nevict, wid, lresume = mess
            sresult, start = outstanding.pop(rreq)
            assert result == sresult, (rreq, result, sresult)
            if show_responses:
                log('response', rreq, site, size, time.time()-start,
                    wtime, n, nhit, nmiss, nevict, wid, lresume)


def worker(id, cache_max, queue_size=5, nsummary=100, time_ring_size=100,
           prefix='worker'):
    id = '%s%s' % (prefix, id)
    log('%s pid=%s' % (id, os.getpid()))
    resume = {}
    resume_gen = 0

    context = zmq.Context()
    broker = context.socket(zmq.XREQ)
    broker.connect(broker_apply_addr)

    broker.send(dumps((id, resume, resume_gen), 1))
    nrequested = 1

    m2 = context.socket(zmq.PUB)
    m2.connect(mongrel2_subresp_addr)

    cache = pylru.lrucache(cache_max)

    time_ring = []
    time_ring_pos = 0

    njobs = 0
    sum_elapsed = sum_oids = sum_hits = sum_miss = sum_evicts = 0
    while 1:
        if njobs%nsummary == 0 and njobs:
            print ' '.join(map(str, (
                id, njobs,
                int(nsummary*60/sum_elapsed),
                sum_oids/nsummary,
                sum_hits/nsummary,
                sum_miss/nsummary,
                sum_evicts/nsummary,
                list(reversed(sorted(map(int, resume.itervalues())))),
                )))
            sum_elapsed = sum_oids = sum_hits = sum_miss = sum_evicts = 0

        job = loads(broker.recv())
        njobs += 1
        nrequested -= 1
        site = job.pop(0)
        if site not in resume:
            resume[site] = 1
            resume_gen += 1

        # request more work while we're working on this request, so we don't
        # have to wait for a round trip when we're ready for more.
        while nrequested < queue_size:
            broker.send(dumps((id, resume, resume_gen), 1))
            nrequested += 1

        nreq = job.pop(0)
        start = time.time()
        n = 0
        nhit = nmiss = nevict = 0
        for oid in job:
            n += 1
            key = site, oid
            if key in cache:
                nhit += 1
            else:
                nmiss += 1
                if len(cache) >= cache_max:
                    nevict += 1
                cache[key] = 1

                # optimistically simulate a db load
                time.sleep(.001)

        elapsed = max(time.time() - start, .0001)

        m2.send(dumps(
            (nreq, sum(job),
             elapsed, n, nhit, nmiss, nevict, id, len(resume))))

        sum_elapsed += elapsed
        sum_oids += n
        sum_hits += nhit
        sum_miss += nmiss
        sum_evicts += nevict

        time_ring_pos = njobs % time_ring_size
        try:
            time_ring[time_ring_pos] = site, elapsed
        except IndexError:
            time_ring.append((site, elapsed))

        if njobs % time_ring_size == 0:
            bysite = {}
            for site, elapsed in time_ring:
                sumn = bysite.get(site)
                if sumn:
                    sumn[0] += elapsed
                    sumn[1] += 1
                else:
                    bysite[site] = [elapsed, 1]
            resume = dict((site, n/sum)
                          for (site, (sum, n)) in bysite.iteritems()
                          )
            resume_gen += 1


def handle_worker(workers_socket, workers_by_addr):
    addr, resume = workers_socket.recv_multipart()
    resume = loads(resume)
    if isinstance(resume, str):
        return resume

    wid, resume, resume_gen = resume

    worker = workers_by_addr.get(addr)
    if worker is None:
        worker = workers_by_addr[addr] = Worker(wid, addr)
    else:
        worker.count += 1

    worker.new_resume(resume, resume_gen)

def handle_m2(m2_socket, workers_by_site, workers, workers_by_addr,
              workers_socket):
    work_message = m2_socket.recv()
    data = loads(work_message)
    site = data[0]
    site_workers = workers_by_site.get(site)
    hit = 0
    if site_workers:
        worker = site_workers[-1][1]
        hit = 1
    else:
        worker = workers[-1][1]

    worker.count -= 1
    if worker.count < 1:
        worker.unregister()
        del workers_by_addr[worker.addr]

    workers_socket.send_multipart([worker.addr, work_message])
    return hit

def dump_profile(profiler, name):
    profiler.disable()
    profiler.dump_stats(name)
    profiler.enable()

def broker(profile=None):
    log('broker pid=%s' % os.getpid())
    context = zmq.Context()
    m2_socket = context.socket(zmq.PULL)
    m2_socket.connect(mongrel2_pushreq_addr)
    workers_socket = context.socket(zmq.XREP)
    workers_socket.bind(broker_apply_addr)

    workers_by_site = {None: []}
    global workers_by_site
    workers = workers_by_site[None]
    workers_by_addr = {}
    availability = {}

    poller = zmq.Poller()
    poller.register(m2_socket, zmq.POLLIN)
    poller.register(workers_socket, zmq.POLLIN)

    nreq = nhit = 0
    lastt = time.time()

    if profile:
        import cProfile
        profiler = cProfile.Profile()
        profiler.enable()

    while 1:

        ready = dict(poller.poll())

        if ready.get(workers_socket) == zmq.POLLIN:
            command = handle_worker(workers_socket, workers_by_addr)
            if command:
                exec command

            # we want to collect resumes before assigning work so as
            # to increase the chance of finding the best worker for
            # the job.
            continue

        if workers and ready.get(m2_socket) == zmq.POLLIN:
            nreq += 1
            nhit += handle_m2(m2_socket, workers_by_site, workers,
                              workers_by_addr, workers_socket)
            if nreq%1000 == 0:
                log('hitrate',
                    100*nhit/nreq,
                    len(workers),
                    len(workers_by_site),
                    int(60*nreq/(time.time()-lastt)),
                    )

class Worker:

    count = 1
    resume_gen = None

    def __init__(self, wid, addr):
        self.wid = wid
        self.addr = addr

    def new_resume(self, resume, resume_gen):
        if resume_gen == self.resume_gen:
            return

        if self.resume_gen is not None:
            self.unregister()

        self.resume = resume
        self.resume_gen = resume_gen
        self.score = - sum(resume.itervalues())
        self.register()

    def register(self):

        def _register(workers, score):
            item = score, self
            index = bisect.bisect_left(workers, item)
            workers.insert(index, item)

        _register(workers_by_site[None], self.score)

        for site, score in self.resume.iteritems():
            site_workers = workers_by_site.get(site)
            if site_workers is None:
                site_workers = workers_by_site[site] = []
            _register(site_workers, score)


    def unregister(self):

        def _unregister(workers, score):
            index = bisect.bisect_left(workers, (score, self))
            del workers[index]


        _unregister(workers_by_site[None], self.score)

        for site, score in self.resume.iteritems():
            site_workers = workers_by_site.get(site)
            if site_workers is None:
                site_workers = workers_by_site[site] = []
            _unregister(site_workers, score)


    def __repr__(self):
        return "worker(%r, %s, %s)" % (
            self.wid, len(self.resume), self.score)

parser = optparse.OptionParser("Usage: %prog [options]")

parser.add_option("--workers", "-w", type="int", default=20)
parser.add_option("--cache-size", "-c", type="int", default=10000)
parser.add_option("--worker-queue-size", "-q", type="int", default=5)

parser.add_option("--sites", "-s", type="int", default=400)
parser.add_option("--oids", type="int", default=10000, help="oids per site")
parser.add_option("--outstanding", "-o", type="int", default=200)
parser.add_option("--min-size", type="int", default=100)
parser.add_option("--max-size", type="int", default=2000)
parser.add_option("--requests", "-R", type="int", default=100000)
parser.add_option("--show-responses", "-r", action='store_true')
parser.add_option("--workers-only")
parser.add_option("--profile")

def main(args=None):
    if args is None:
        args = sys.argv[1:]

    print args
    options, args = parser.parse_args(args)

    Process = multiprocessing.Process

    if not options.workers_only:
        mongrel_process = Process(
            target=mongrel2,
            kwargs=dict(
                nsites=options.sites,
                noids=options.oids,
                nout=options.outstanding,
                minsize=options.min_size,
                maxsize=options.max_size,
                max_requests=options.requests,
                show_responses=options.show_responses,
                ))
        mongrel_process.start()

        p = Process(
            target=broker,
            kwargs=dict(
                profile=options.profile,
                ),
            )
        p.daemon = True
        p.start()

    global new_worker_process
    def new_worker_process(
        id,
        cache_max=options.cache_size,
        queue_size=options.worker_queue_size,
        prefix=options.workers_only or 'worker',
        daemon=True
        ):
        p = Process(
            target=worker, kwargs=dict(
                id=i,
                cache_max=cache_max,
                queue_size=queue_size,
                prefix=prefix
                ))
        p.daemon = daemon
        p.start()

    for i in range(options.workers):
        new_worker_process(id=i, daemon = not options.workers_only)

    if not options.workers_only:
        mongrel_process.join()

def broker_exec():
    context = zmq.Context()
    broker = context.socket(zmq.XREQ)
    broker.connect(broker_apply_addr)
    for arg in sys.argv[1:]:
        broker.send(dumps(arg))
    broker.close()

def m2_exec():
    context = zmq.Context()
    m2 = context.socket(zmq.PUB)
    m2.connect(mongrel2_subresp_addr)
    for arg in sys.argv[1:]:
        m2.send(dumps(arg))
    m2.close()
