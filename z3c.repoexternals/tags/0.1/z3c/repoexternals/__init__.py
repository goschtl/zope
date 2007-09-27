#!/usr/bin/python
"""Recursively retrieves subversion directory listings from the url or
path and matches directories against a previous set of svn:externals
if provided then against regular expressions and generates qualifying
svn:externals lines.  The defaults generate a set of svn:externals for
all the trunks in a repository and keeps them up to date with the
repository as new trunks are added when the previous externals are
provided thereafter."""

import sys, os, re, logging, thread, threading, Queue, optparse
import pysvn

usage = "usage: %prog [options] url_or_path"

parser = optparse.OptionParser(usage=usage, description=__doc__)

parser.add_option(
    "-v", "--verbose", action="count",
    help=("Output logging to stdandard error. Set twice to log "
          "debugging mesages.")) 

parser.add_option(
    "-p", "--previous", metavar='FILE',
    help=("""If provided, only URLs in the repository not 
included in the previous externals will be included. If the filename
is '-', use standard input.  Valid svn:externals lines beginning with
one comment character, '#', will also affect output.  This is useful,
for example, to prevent lengthy recursions into directories that are
known not to contain any desired matches.  The file is read completely
and closed before anything is output, so it is safe to append output
to the previous file: "repoexternals -p EXTERNALS.txt
http://svn.foo.org/repos/main >>EXTERNALS.txt"."""))

include = r'(?i)^((.*)/.+?|.*)/trunk$'
parser.add_option(
    "-i", "--include", default=include, metavar='REGEXP',
    help=("Directory names matching this python regular expression "
          "will be included in output and will not be descended into."
          "  [default: %default]"))

exclude = (r'(?i)^.*/(branch(es)?|tags?|releases?|vendor|bundles?'
           r'|sandbox|build|dist)$')
parser.add_option(
    "-e", "--exclude", default=exclude, metavar='REGEXP',
    help=("Directory names matching this python regular expression "
          "will be excluded from output and will not be descended "
          "into. Include overrides exclude.  [default: %default]"))

matched_template = r'\1'
parser.add_option(
    "-m", "--matched-template", default=matched_template,
    metavar='TEMPLATE',
    help=("""The result of expanding previous file URL matches with
the include regular expression through this template is added to the
set of previous URLs excluded from output and descending.  The default
will add the parents of trunks to the set of previous URLs
excluded.  [default: %default]"""))

parent_template = r'\2'
parser.add_option(
    "-t", "--parent-template", default=parent_template,
    metavar='TEMPLATE',
    help=("""The result of expanding previous file URL matches with
the include regular expression through this template is removed from
the set of matched previous URLs excluded from output and descending.
The default ensures that directories containing trunks within a
directory that contains a trunk are not excluded.
[default: %default]"""))

depth = 5
parser.add_option(
    "-d", "--depth", type="int", default=depth, metavar='INT',
    help=("The maximum directory depth to descend to.  WARNING: "
          "large values can greatly increase run time.  "
          "[default: %default]"))

pool_size = 5
parser.add_option(
    "-s", "--pool-size", type="int", default=pool_size, metavar='INT',
    help=("The number of concurrent svn clients.  WARNING: large "
          "values can DOS the repository.  [default: %default]"))

shutdown = object()
class Thread(threading.Thread):

    def __init__(self, queue=None, results=None, **kwargs):
        super(Thread, self).__init__(**kwargs)
        if queue is None:
            queue = Queue.Queue()
        if results is None:
            results = Queue.Queue()
        self.queue = queue
        self.results = results

    def run(self):
        try:
            payload = self.queue.get()
            while payload is not shutdown:
                payload(self)
                payload = self.queue.get()
        except:
            thread.interrupt_main()
            raise

    def shutdown(self):
        self.queue.put(shutdown)
        self.join()

    def interrupt(self):
        self.queue.mutex.acquire()
        self.queue._init(self.queue.maxsize)
        self.queue._put(shutdown)
        self.queue.not_empty.notify()
        self.queue.mutex.release()
        self.join()

class ClientThread(Thread):

    def __init__(self, *args, **kwargs):
        super(ClientThread, self).__init__(*args, **kwargs)
        self.client = pysvn.Client()

class ClientPool(Queue.Queue):

    def __init__(self, size=pool_size, results=None,
                 **kwargs):
        Queue.Queue.__init__(self, **kwargs)
        if results is None:
            results = Queue.Queue()
        self.results = results
        self.threads = [
            ClientThread(queue=self, results=self.results)
            for ignored in xrange(size)]

    def start(self):
        for thread in self.threads:
            thread.start()
        logging.getLogger('repoexternals').debug(
            'Started %s client threads' % len(self.threads))

    def shutdown(self):
        for thread in self.threads:
            self.put(shutdown)
        for thread in self.threads:
            thread.join()

    def interrupt(self):
        self.mutex.acquire()
        self._init(self.maxsize)
        for thread in self.threads:
            self._put(shutdown)
        self.not_empty.notify()
        self.mutex.release()
        for thread in self.threads:
            if thread.isAlive():
                thread.join()

class Root(object):
    """Return self unless overriden in a child instance"""

    def __get__(self, instance, owner):
        return instance

class Line(object):

    def __init__(self, path, dirent):
        self.path = path
        self.dirent = dirent

    def __str__(self):
        return '%s %s' % (self.path, self.dirent.path)

class Listing(object):
    """A single svn listing"""

    def __init__(self, url, include=include, exclude=exclude,
                 depth=depth):
        self.url = url
        self.include = re.compile(include)
        self.exclude = re.compile(exclude)
        self.depth = depth

        self.results = Queue.Queue()

    def list(self, thread):
        """Retrieve the svn listing from the repository"""
        try:
            self.listing = thread.client.list(
                self.url, dirent_fields=pysvn.SVN_DIRENT_KIND)
        except pysvn.ClientError, e:
            logging.getLogger('repoexternals').exception(
                'pysvn.ClientError %s' % self.url)
            self.listing = []

        # Queue for processing
        thread.results.put(self.process)

    root = Root()

    def getchild(self, url):
        """Create and return a child listing setting it's root"""
        child = Listing(url, include=self.include,
                        exclude=self.exclude, depth=self.depth)
        child.root = self.root
        return child
    
    def process(self, thread):
        """Process the results of the svn listing"""

        # Use local names in the inner loop
        dir_node_kind = pysvn.node_kind.dir
        root_url = self.root.url
        include_match = self.include.match
        exclude_match = self.exclude.match
        results_put = self.results.put
        lLine = Line
        info = logging.getLogger('repoexternals').info
        depth = self.depth
        getchild = self.getchild
        thread_results_put = thread.results.put
        previous = self.root.previous

        for dirent, ignored in self.listing[1:]:

            if dirent.kind != dir_node_kind:
                # externals can only be directories
                continue

            dirent_path = dirent.path

            if dirent_path in previous:
                info('In previous, skipping %s' % dirent_path)
                continue

            # No previous line, use matching
            path = dirent_path[len(root_url):].lstrip('/')

            if include_match(dirent_path) is not None:
                # Include this line in the results
                results_put(lLine(path=path, dirent=dirent))

            elif exclude_match(dirent_path) is not None:
                info('Excluding %s' % dirent_path)
            elif len(path.split('/')) >= depth:
                info('Too deep, skipping %s' % dirent_path)

            else:
                child = getchild(dirent_path)
                info('Descending into %s' % dirent_path)
                thread_results_put(child.list)
                results_put(child)

        # Let the iterator know we're done
        results_put(shutdown)

    def __iter__(self):
        item = self.results.get()
        while item is not shutdown:
            if isinstance(item, Line):
                yield item
            else:
                for child in item:
                    yield child
            item = self.results.get()

# Match valid externals definitions in existing externals
external = re.compile(r'^\s*#?\s*([^#\s]+)\s(.*\s|)(\S+)\s*$')

def run(url, previous=(), include=include, exclude=exclude,
        matched_template=matched_template,
        parent_template=parent_template,
        depth=depth, pool_size=pool_size):
    pool = ClientPool(size=pool_size)
    thread = Thread(queue=pool.results, results=pool)

    pool.start()
    thread.start()

    try:
        root = Listing(url, include=include, exclude=exclude,
                       depth=depth)

        # Build the set of previous URLs
        include_match = root.include.match
        root.previous = set()
        raw_add = root.previous.add
        matched = set()
        matched_add = matched.add
        parents = set()
        parents_add = parents.add
        external_match = external.match
        for line in previous:
            match = external_match(line)
            if match is not None:
                # TODO: also use pysvn.Cliens.is_url to verify url
                # validity?
                line_url = match.group(3)
                raw_add(line_url)
                include_matched = include_match(line_url)
                if include_matched is not None:
                    matched_add(
                        include_matched.expand(matched_template))
                    parents_add(
                        include_matched.expand(parent_template))
        root.previous.update(matched.difference(parents))

        pool.put(root.list)

        for line in root:
            yield line
    except:
        # TODO: can't find a way to test interruptability
        pool.interrupt()
        thread.interrupt()
        raise
    else:
        pool.shutdown()
        thread.shutdown()

def main():
    options, args = parser.parse_args()

    if len(args) != 1:
        parser.error("requires one url_or_path")
    url, = args

    if options.verbose is not None:
        verbose = options.verbose <= 2 and options.verbose or 2
        logging.basicConfig(level=logging.WARN - (verbose * 10))

    previous = ()
    if options.previous:
        if options.previous == '-':
            previous = sys.stdin
        else:
            previous = file(options.previous)

    for line in run(url, previous, options.include, options.exclude,
                    options.matched_template, options.parent_template,
                    options.depth, options.pool_size):
        print line

if __name__ == '__main__':
    main()
