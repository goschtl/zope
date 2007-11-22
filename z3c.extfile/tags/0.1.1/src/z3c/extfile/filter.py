import os.path
from z3c.extfile import processor, hashdir
from cStringIO import StringIO
import mimetypes

BLOCK_SIZE = 1024*128

class FSFilter(object):

    def __init__(self, app, directory=None):
        self.app = app
        if directory is not None:
            # use provided directory
            self.dir = os.path.abspath(directory)
        else:
            #use environment variable
            if not os.environ.has_key('EXTFILE_STORAGEDIR'):
                raise RuntimeError, "EXTFILE_STORAGEDIR not defined"
            self.dir = os.environ.get('EXTFILE_STORAGEDIR')
        self.hd = hashdir.HashDir(self.dir)

    def __call__(self, env, start_response):
        if env.get('REQUEST_METHOD')=='POST' and \
           env.get('CONTENT_TYPE','').startswith('multipart/form-data;'):
            fp = env['wsgi.input']
            out = StringIO()
            proc = processor.Processor(self.hd)
            proc.pushInput(fp, out)
            out.seek(0)
            env['wsgi.input'] = out
        elif env.get('REQUEST_METHOD') in ('GET',):
            resp = FileResponse(self.app, self.hd)
            return resp(env, start_response)
        return self.app(env, start_response)

class FileResponse(object):

    def __init__(self, app, hd):
        self.hd = hd
        self.app = app

    def start_response(self, status, headers_out, exc_info=None):
        """Intercept the response start from the filtered app."""
        self.status      = status
        self.headers_out = headers_out
        self.exc_info    = exc_info

    def __call__(self, env, start_response):
        """Facilitate WSGI API by providing a callable hook."""
        self.env        = env
        self.real_start = start_response
        return self.__iter__()

    def __iter__(self):

        result = self.app(self.env, self.start_response)
        result_iter  = result.__iter__()
        doHandle = False
        for n,v in self.headers_out:
            # the length is digest(40) + len(z3c.extfile.digest)
            if n.lower()=='content-length' and v=='59':
                doHandle = True
                break
        if not doHandle:
            # this is not for us
            headers_out = self.headers_out
            iter_out = result_iter
        else:
            headers_out = dict(
                [(k.lower(),v) for k,v in self.headers_out]
                )

            body = "".join(result_iter)
            if body.startswith('z3c.extfile.digest:'):
                digest = body[19:]
            else:
                digest = None
            # do we have to handle the content. type?
            # zope sniffs if it has no extension, so we get an unknown
            # text content-type for our digest
            filename = self.env['PATH_INFO']
            content_type, content_encoding =mimetypes.guess_type(filename)
            if content_type and not 'unknown' in \
                   headers_out.get('content-type','unknown'):
                headers_out['content-type'] = content_type
            if content_encoding and not 'content-encoding' in headers_out:
                headers_out['content-encoding'] = content_encoding
            if digest is not None:
                try:
                    size = self.hd.getSize(digest)
                    headers_out['content-length'] = size
                    f = self.hd.open(digest)
                    fw = self.env.get('wsgi.file_wrapper')
                    iter_out = fw(f, BLOCK_SIZE)
                except KeyError:
                    # no such digest available, just return the body
                    iter_out = body.__iter__()
            else:
                # we have no digest so return body
                iter_out = body.__iter__()
            headers_out = headers_out.items()
        self.real_start(self.status, headers_out, exc_info=self.exc_info)
        return iter_out


def filter_factory(global_conf, **local_conf):
    def filter(app):
        return FSFilter(app, **local_conf)
    return filter



