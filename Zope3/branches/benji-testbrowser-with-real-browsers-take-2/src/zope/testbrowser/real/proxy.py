import BaseHTTPServer
import Queue
import SocketServer
import cgi
import httplib
import os
import select
import simplejson
import socket
import threading
import urlparse
from zope.app.testing import functional
from StringIO import StringIO

base_dir = os.path.dirname(__file__)
allowed_resources = ['MochiKit', 'shim.js', 'commands.js', 'start.html']

PROXY_PORT = 23123
PROXY_HOST = '127.0.0.1'

class Constant(object):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

UNDEFINED = Constant('undefined')

class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
#    server_version = "TinyHTTPProxy/" + __version__
    rbufsize = 0

    def __init__(self, request, client_address, server):
        self.caller = functional.HTTPCaller()
        self.command_queue = server.command_queue
        self.result_queue = server.result_queue
        BaseHTTPServer.BaseHTTPRequestHandler.__init__(
            self, request, client_address, server)

    def _connect(self, netloc, soc):
        if ':' in netloc:
            i = netloc.index(':')
            host_and_port = netloc[:i], int(netloc[i+1:])
        else:
            host_and_port = netloc, 80
        try:
            soc.connect(host_and_port)
        except socket.error, arg:
            try:
                msg = arg[1]
            except:
                msg = arg
            self.send_error(404, msg)
            return False
        return True

    def sendFile(self, path):
        assert path.startswith('/')
        path = path[1:]
        assert path.split('/')[1] in allowed_resources
        # XXX might use too much memory
        self.wfile.write(open(os.path.join(base_dir, path)).read())

    def handleRequest(self):
        (scheme, netloc, path, params, query, fragment) = urlparse.urlparse(
            self.path, 'http')
        assert netloc == ''
#        print self.path
        if scheme != 'http':
            self.send_error(400, "unknown scheme %r" % scheme)
            return
        self.log_request()

        if self.command in ('GET', 'POST'):
            if path.startswith('/__resources__/'):
                self.sendFile(path)
                return
            elif path.startswith('/__api__/'):
                operation = urlparse.urlparse(self.path)[2].split('/')[-1]
                raw_json = self.rfile.next()

                if raw_json.strip() == 'undefined':
                    last_result = UNDEFINED
                else:
                    last_result = simplejson.loads(raw_json)

                if operation == 'next':
                    # if no command has been processed yet, the last_result
                    # value will be a placeholder
                    if last_result != '__testbrowser__no_result_yet':
                        self.result_queue.put(last_result)

                    response = self.command_queue.get()
                    if response[0] == '_tb_stop':
                        self.server.stop = True
                        self.result_queue.put('the server has stopped')
                else:
                    self.send_response(404)
                    self.send_header('Content-Type', 'text/plain')
                    self.end_headers()
                    msg = 'unknown operation: %r' % operation
                    self.wfile.write(msg)
                    raise RuntimeError(msg)

                self.send_response(200)
                self.send_header('Content-Type', 'text/plain')
                self.end_headers()
                self.wfile.write(simplejson.dumps(response))
                import time;time.sleep(1)
                return

        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
#            print 'sending', self.remote_host
            request = StringIO()
            request.write("%s %s %s\r\n" % (
                self.command,
                urlparse.urlunparse(('', '', path, params, query, '')),
                self.request_version))
            self.headers['Connection'] = 'close'
            for key_val in self.headers.items():
                request.write("%s: %s\r\n" % key_val)
            request.write("\r\n")
            response = self.caller(request.getvalue())
            self.connection.send(response.getOutput())
#            print 'done with', self.path
        finally:
            self.connection.close()

    do_HEAD = do_POST = do_PUT = do_DELETE = do_GET = handleRequest

    def do_NOOP(self):
        self.send_response(200)
        self.end_headers()

    def log_message(self, format, *args):
        pass


class HttpServer(SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer):

    stop = False

    def __init__(self, *args, **kws):
        self.command_queue = Queue.Queue()
        self.result_queue = Queue.Queue()
        self.threads = []
        BaseHTTPServer.HTTPServer.__init__(self, *args, **kws)

    def serve_forever(self):
        """Handle one request at a time until stopped."""
        while not self.stop:
            self.handle_request()

    # This method comes from ThreadingMixIn
    def process_request_thread(self, request, client_address):
        my_thread = threading.currentThread()
        self.threads.append(my_thread)
        return SocketServer.ThreadingMixIn.process_request_thread(
            self, request, client_address)


class ServerManager(object):
    def __init__(self):
        self.host = PROXY_HOST
        self.port = PROXY_PORT
        self.server = HttpServer((self.host, self.port), RequestHandler)

    def start(self):
        self.server_thread = threading.Thread(
                                target=self.server.serve_forever)
        self.server_thread.setDaemon(True)
        self.server_thread.start()

    def stop(self):
        self.executeCommand('stop')
        conn = httplib.HTTPConnection('%s:%d' % (self.host, self.port))
        conn.request('NOOP', '/')
        conn.getresponse()

        # we want to wait until all outstanding requests are finished before
        # we return
        for t in self.server.threads:
            t.join()

        self.server_thread.join()

    def executeCommand(self, command, *args):
        self.server.command_queue.put( ('_tb_'+command, simplejson.dumps(args)) )
        return self.server.result_queue.get()
