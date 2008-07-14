import os.path
from z3c.extfile import processor, hashdir
from cStringIO import StringIO
import mimetypes
import interfaces
from  zope.cachedescriptors.property import Lazy
BLOCK_SIZE = 1024*128

class FSFilter(object):

    def __init__(self, app, directory=None):

        self.app = app
        if directory is not None:
            # use provided directory
            self.dir = os.path.abspath(directory)
        else:
            self.dir = None

    @Lazy
    def hd(self):
        if self.dir is None:
            #use environment variable
            if not os.environ.has_key('EXTFILE_STORAGEDIR'):
                raise RuntimeError, "EXTFILE_STORAGEDIR not defined"
            self.dir = os.environ.get('EXTFILE_STORAGEDIR')
        return hashdir.HashDir(self.dir)

    def __call__(self, env, start_response):
        method = env.get('REQUEST_METHOD')
        if env.get('HTTP_X_EXTFILE_HANDLE'):
            if method=='POST' and \
                   env.get('CONTENT_TYPE','').startswith('multipart/form-data;'):
                fp = env['wsgi.input']
                out = StringIO()
                proc = processor.Processor(
                    self.hd,
                    contentInfo=env.has_key('HTTP_X_EXTFILE_INFO'),
                    allowedTypes=env.get('HTTP_X_EXTFILE_TYPES'),
                    )
                cl = env.get('CONTENT_LENGTH')
                if not cl:
                    raise RuntimeError, "No content-length header found"
                cl = int(cl)
                try:
                    proc.pushInput(fp, out, cl)
                except interfaces.TypeNotAllowed:
                    start_response("400 Bad Request", [
                        ('Content-Type', 'text/plain')])
                    return []
                env['CONTENT_LENGTH'] = out.tell()
                out.seek(0)
                env['wsgi.input'] = out
            elif method == 'GET':
                resp = FileResponse(self.app, self.hd)
                return resp(env, start_response)
        return self.app(env, start_response)

def getInfo(s):

    """takes a z3c.extfile info string and returns a (digest,
    contentType, contentLength) tuple. If the parsing fails digest is
    None"""

    parts = s.split(':')
    contentType = contentLength = None
    if len(parts)==2:
        digest = parts[1]
    elif len(parts)==4:
        digest, contentType, contentLength = parts[1:]
    else:
        digest = None
    if digest and len(digest)!=40:
        digest = None
    if contentLength is not None:
        try:
            contentLength=int(contentLength)
        except ValueError:
            contentLength = None
    return (digest, contentType, contentLength)

class FileResponse(object):

    def __init__(self, app, hd):
        self.hd = hd
        self.app = app

    def start_response(self, status, headers_out, exc_info=None):
        """Intercept the response start from the filtered app."""
        self.doHandle = False
        if '200' in status:
            for n,v in headers_out:
                # the length is digest(40) + len(z3c.extfile.digest)
                # we do not now how long the info is getting but it should
                # be under 100
                if n.lower()=='content-length' and len(v)<3:
                    self.doHandle = True
                    break
        self.status      = status
        self.headers_out = headers_out
        self.exc_info    = exc_info

    def __call__(self, env, start_response):
        """Facilitate WSGI API by providing a callable hook."""
        self.env        = env
        self.real_start = start_response
        self.response = self.app(self.env, self.start_response)
        if self.doHandle is False:
            return self._orgStart()
        body = "".join(self.response)
        self.response = [body]
        if not body.startswith('z3c.extfile.digest:'):
            return self._orgStart()
        digest, contentType, contentLength = getInfo(body)
        if digest is None:
            return self._orgStart()
        try:
            f = self.hd.open(digest)
        except KeyError:
            # no such digest
            return self._orgStart()
        headers_out = dict(
            [(k.lower(),v) for k,v in self.headers_out]
            )
        if contentType:
            headers_out['content-type'] = contentType
        if contentLength:
            headers_out['content-length'] = str(contentLength)
        else:
            headers_out['content-length'] = str(len(f))
        headers_out = headers_out.items()
        self.real_start(self.status, headers_out, self.exc_info)
        return f.__iter__()

    def _orgStart(self):
        self.real_start(self.status, self.headers_out, self.exc_info)
        return self.response

def filter_factory(global_conf, **local_conf):
    if local_conf.has_key('directory'):
        local_conf['directory'] = os.path.join(
            global_conf.get('here'), local_conf.get('directory'))
    def filter(app):
        return FSFilter(app, **local_conf)
    return filter



