# S3 blob test
import boto.s3.connection
import boto.s3.key
import os
import re
import sys
import tempfile
import time
import ZEO.StorageServer

# copy script that gets around the fact that we haven't implemented
# committing blobs.

hexmatch = re.compile('0x([0-9a-fA-F]{2})$').match

def copy_blobs(args=None):
    if args is None:
        args = sys.argv[1:]
    [blob_dir] = args

    bucket_name, folder = os.environ['S3_FOLDER'].split('/', 1)

    conn = boto.s3.connection.S3Connection()
    bucket = conn.get_bucket(bucket_name)
    prefix = blob_dir
    if not prefix.endswith('/'):
        prefix += '/'
    lprefix = len(prefix)

    key = boto.s3.key.Key(bucket)

    logfile = open("/tmp/copy_blobs_to_s3-%s-%s-%s.log"
                   % (bucket_name, folder, time.time()),
                   'w')

    for dirpath, dirs, files in os.walk(blob_dir):
        for n in files:
            if not n.endswith('.blob'):
                continue
            p = os.path.join(dirpath, n)
            oid = ''.join(hexmatch(seg).group(1)
                          for seg in dirpath[lprefix:].split('/')
                          )
            serial = n[2:-5]
            key.key = "%s/%s/%s" % (folder, oid, serial)
            t = time.time()
            key.set_contents_from_filename(p)
            sz = os.stat(p).st_size
            print >>logfile, int((time.time()-t)*1000000), sz

# Monkey patch that lods blobs from s

def patch():

    bucket_name, folder = os.environ['S3_FOLDER'].split('/', 1)

    def sendBlob(self, oid, serial):
        try:
            key = self._s3key
        except AttributeError:
            conn = boto.s3.connection.S3Connection()
            bucket = self._s3bucket = conn.get_bucket(bucket_name)
            key = self._s3key = boto.s3.key.Key(
                boto.s3.connection.S3Connection().get_bucket(bucket_name)
                )
        key.key = "%s/%s/%s" % (folder, oid.encode('hex'), serial.encode('hex'))
        f = tempfile.TemporaryFile()
        key.get_contents_to_file(f)
        f.seek(0)

        def store():
            yield ('receiveBlobStart', (oid, serial))
            while 1:
                chunk = f.read(59000)
                if not chunk:
                    break
                yield ('receiveBlobChunk', (oid, serial, chunk, ))
            f.close()
            yield ('receiveBlobStop', (oid, serial))

        self.client.rpc.callAsyncIterator(store())

    ZEO.StorageServer.ZEOStorage.sendBlob = sendBlob
