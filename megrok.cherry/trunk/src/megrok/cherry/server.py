import cherrypy
from zope.app.wsgi import getWSGIApplication
from StringIO import StringIO
from cherrypy import wsgi, _cpwsgiserver
from zope.component import event # XXX voodoo necessary to make events work

def startServer():
    f = StringIO('''
    site-definition /home/faassen/buildout/megrok.cherry/site.zcml
    
    <zodb>
      <filestorage>
        path /home/faassen/buildout/megrok.cherry/parts/data/Data.fs
      </filestorage>
    </zodb>

    <eventlog>
      <logfile>
        path STDOUT
      </logfile>
    </eventlog>
    ''')
    app = getWSGIApplication(f)
    
    f.close()
    server = WSGIServer(app)
    try:
        server.start()
    except (KeyboardInterrupt, SystemExit):
        server.stop()
        
class WSGIServer(wsgi.WSGIServer):
    def __init__(self, app):
        server = cherrypy.server
        sockFile = server.socket_file
        if sockFile:
            bind_addr = sockFile
        else:
            bind_addr = (server.socket_host, server.socket_port)
        s = _cpwsgiserver.CherryPyWSGIServer
        s.__init__(self, bind_addr,
                   app,
                   server.thread_pool,
                   server.socket_host,
                   request_queue_size = server.socket_queue_size,
                   timeout = server.socket_timeout,
                   )
        self.protocol = server.protocol_version
        self.ssl_certificate = server.ssl_certificate
        self.ssl_private_key = server.ssl_private_key

