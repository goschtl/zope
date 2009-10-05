##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

import cPickle
import logging
import os
import subprocess
import sys

from ZODB.FileStorage.format import FileStorageFormatter, CorruptedDataError
from ZODB.utils import p64, u64, z64
from ZODB.FileStorage.format import TRANS_HDR_LEN

import ZODB.FileStorage
import ZODB.FileStorage.fspack
import ZODB.fsIndex
import ZODB.TimeStamp

class FileStoragePacker(FileStorageFormatter):

    def __init__(self, path, stop, la, lr, cla, clr, current_size):
        self._name = path
        # We open our own handle on the storage so that much of pack can
        # proceed in parallel.  It's important to close this file at every
        # return point, else on Windows the caller won't be able to rename
        # or remove the storage file.
        self._file = open(path, "rb")

        self._stop = stop
        self.locked = 0
        self.file_end = current_size

        # The packer needs to acquire the parent's commit lock
        # during the copying stage, so the two sets of lock acquire
        # and release methods are passed to the constructor.
        self._lock_acquire = la
        self._lock_release = lr
        self._commit_lock_acquire = cla
        self._commit_lock_release = clr

        self.ltid = z64

    def pack(self):

        script = self._name+'.packscript'
        open(script, 'w').write(pack_script_template % dict(
            path = self._name,
            stop = self._stop,
            size = self.file_end,
            syspath = sys.path,
            ))
        for name in 'error', 'log':
            name = self._name+'.pack'+name
            if os.path.exists(name):
                os.remove(name)
        proc = subprocess.Popen(
            (sys.executable, script),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            close_fds=True,
            )


        proc.stdin.close()
        out = proc.stdout.read()
        if proc.wait():
            if os.path.exists(self._name+'.packerror'):
                v = cPickle.Unpickler(open(self._name+'.packerror', 'rb')
                                      ).load()
                os.remove(self._name+'.packerror')
                raise v
            raise RuntimeError('The Pack subprocess failed\n'
                               +'-'*60+out+'-'*60+'\n')

        packindex_path = self._name+".packindex"
        if not os.path.exists(packindex_path):
            return # already packed or pack didn't benefit

        index, opos = cPickle.Unpickler(open(packindex_path, 'rb')).load()
        os.remove(packindex_path)
        os.remove(self._name+".packscript")

        output = OptionalSeekFile(self._name + ".pack", "r+b")
        output.seek(0, 2)
        assert output.tell() == opos
        self.copyRest(self.file_end, output, index)

        # OK, we've copied everything. Now we need to wrap things up.
        pos = output.tell()
        output.close()

        # Grrrrr. The caller wants these attrs
        self.index = index
        self.vindex = {}
        self.tindex = {}
        self.tvindex = {}
        self.oid2tid = {}
        self.toid2tid = {}
        self.toid2tid_delete = {}

        return pos

    def copyRest(self, input_pos, output, index):
        # Copy data records written since packing started.

        self._commit_lock_acquire()
        self.locked = 1
        # Re-open the file in unbuffered mode.

        # The main thread may write new transactions to the file,
        # which creates the possibility that we will read a status
        # 'c' transaction into the pack thread's stdio buffer even
        # though we're acquiring the commit lock.  Transactions
        # can still be in progress throughout much of packing, and
        # are written to the same physical file but via a distinct
        # Python file object.  The code used to leave off the
        # trailing 0 argument, and then on every platform except
        # native Windows it was observed that we could read stale
        # data from the tail end of the file.
        self._file = OptionalSeekFile(self._name, "rb", 0)
        try:
            try:
                while 1:
                    # The call below will raise CorruptedDataError at EOF.
                    input_pos = self._copyNewTrans(
                        input_pos, output, index,
                        self._commit_lock_acquire, self._commit_lock_release)
            except CorruptedDataError, err:
                # The last call to copyOne() will raise
                # CorruptedDataError, because it will attempt to read past
                # the end of the file.  Double-check that the exception
                # occurred for this reason.
                self._file.seek(0, 2)
                endpos = self._file.tell()
                if endpos != err.pos:
                    raise
        finally:
            self._file.close()

    def _copyNewTrans(self, input_pos, output, index,
                      acquire=None, release=None):
        tindex = {}
        copier = PackCopier(output, index, {}, tindex, {})
        th = self._read_txn_header(input_pos)
        if release is not None:
            release()

        output_tpos = output.tell()
        copier.setTxnPos(output_tpos)
        output.write(th.asString())
        tend = input_pos + th.tlen
        input_pos += th.headerlen()
        while input_pos < tend:
            h = self._read_data_header(input_pos)
            prev_txn = None
            if h.plen:
                data = self._file.read(h.plen)
            else:
                # If a current record has a backpointer, fetch
                # refs and data from the backpointer.  We need
                # to write the data in the new record.
                data = self.fetchBackpointer(h.oid, h.back)
                if h.back:
                    prev_txn = self.getTxnFromData(h.oid, h.back)

            if h.version:
                self.fail(pos, "Versions are not supported.")

            copier.copy(h.oid, h.tid, data, '', prev_txn,
                        output_tpos, output.tell())

            input_pos += h.recordlen()

        output_pos = output.tell()
        tlen = p64(output_pos - output_tpos)
        output.write(tlen)
        output_pos += 8

        if tlen != th.tlen:
            # Update the transaction length
            output.seek(output_tpos + 8)
            output.write(tlen)
            output.seek(output_pos)

        index.update(tindex)
        tindex.clear()

        if acquire is not None:
            acquire()

        return input_pos + 8

    def fetchBackpointer(self, oid, back):
        if back == 0:
            return None
        data, tid = self._loadBackTxn(oid, back, 0)
        return data

# sys.modules['ZODB.FileStorage.FileStorage'
#             ].FileStoragePacker = FileStoragePacker
# ZODB.FileStorage.FileStorage.supportsVersions = lambda self: False

class PackCopier(ZODB.FileStorage.fspack.PackCopier):

    def _txn_find(self, tid, stop_at_pack):
        # _pos always points just past the last transaction
        pos = self._pos
        while pos > 4:
            self._file.seek(pos - 8)
            pos = pos - u64(self._file.read(8)) - 8
            self._file.seek(pos)
            h = self._file.read(TRANS_HDR_LEN)
            _tid = h[:8]
            if _tid == tid:
                return pos
            if stop_at_pack:
                if h[16] == 'p':
                    break

        return None


pack_script_template = """

import sys, logging

sys.path[:] = %(syspath)r

import cPickle
import zc.FileStorage

logging.getLogger().setLevel(logging.INFO)
handler = logging.FileHandler(%(path)r+'.packlog')
handler.setFormatter(logging.Formatter(
   '%%(asctime)s %%(name)s %%(levelname)s %%(message)s'))
logging.getLogger().addHandler(handler)

try:
    packer = zc.FileStorage.PackProcess(%(path)r, %(stop)r, %(size)r)
    packer.pack()
except Exception, v:
    logging.exception('packing')
    try:
        v = cPickle.dumps(v)
    except Exception:
        pass
    else:
        open(%(path)r+'.packerror', 'w').write(v)
    raise
"""

class PackProcess(FileStoragePacker):

    def __init__(self, path, stop, current_size):
        self._name = path
        # We open our own handle on the storage so that much of pack can
        # proceed in parallel.  It's important to close this file at every
        # return point, else on Windows the caller won't be able to rename
        # or remove the storage file.

        # We set the buffer quite high (32MB) to try to reduce seeks
        # when the storage is disk is doing other io


        self._file = OptionalSeekFile(path, "rb")

        self._name = path
        self._stop = stop
        self.locked = 0
        self.file_end = current_size

        self.ltid = z64

        self._freecache = _freefunc(self._file)
        logging.info('packing to %s',
                     ZODB.TimeStamp.TimeStamp(self._stop))

    def _read_txn_header(self, pos, tid=None):
        self._freecache(pos)
        return FileStoragePacker._read_txn_header(self, pos, tid)

    def _log_memory(self): # only on linux, oh well
        status_path = "/proc/%s/status" % os.getpid()
        if not os.path.exists(status_path):
            return
        try:
            f = open(status_path)
        except IOError:
            return

        for line in f:
            for name in ('Peak', 'Size', 'RSS'):
                if line.startswith('Vm'+name):
                    logging.info(line.strip())


    def pack(self):
        packed, index, packpos = self.buildPackIndex(self._stop, self.file_end)
        logging.info('initial scan %s objects at %s', len(index), packpos)
        self._log_memory()
        if packed:
            # nothing to do
            logging.info('done, nothing to do')
            self._file.close()
            return

        self._log_memory()
        logging.info('copy to pack time')
        output = OptionalSeekFile(self._name + ".pack", "w+b")
        output._freecache = _freefunc(output)
        index, new_pos = self.copyToPacktime(packpos, index, output)
        self._log_memory()
        if new_pos == packpos:
            # pack didn't free any data.  there's no point in continuing.
            self._file.close()
            output.close()
            os.remove(self._name + ".pack")
            logging.info('done, no decrease')
            return

        logging.info('copy from pack time')
        self.copyFromPacktime(packpos, self.file_end, output, index)
        self._log_memory()

        # Save the index so the parent process can use it as a starting point.
        f = open(self._name + ".packindex", 'wb')
        cPickle.Pickler(f, 1).dump((index, output.tell()))
        f.close()
        output.flush()
        os.fsync(output.fileno())
        output.close()
        self._file.close()


    def buildPackIndex(self, stop, file_end):
        index = ZODB.fsIndex.fsIndex()
        pos = 4L
        packed = True

        while pos < file_end:
            th = self._read_txn_header(pos)
            if th.tid > stop:
                break
            self.checkTxn(th, pos)
            if th.status != "p":
                packed = False

            tpos = pos
            end = pos + th.tlen
            pos += th.headerlen()

            while pos < end:
                dh = self._read_data_header(pos)
                self.checkData(th, tpos, dh, pos)
                if dh.version:
                    self.fail(pos, "Versions are not supported")
                index[dh.oid] = pos
                pos += dh.recordlen()

            tlen = self._read_num(pos)
            if tlen != th.tlen:
                self.fail(pos, "redundant transaction length does not "
                          "match initial transaction length: %d != %d",
                          tlen, th.tlen)
            pos += 8

        return packed, index, pos

    def copyToPacktime(self, packpos, index, output):
        pos = new_pos = self._metadata_size
        self._file.seek(0)
        output.write(self._file.read(self._metadata_size))
        new_index = ZODB.fsIndex.fsIndex()

        while pos < packpos:
            th = self._read_txn_header(pos)
            new_tpos = 0L
            tend = pos + th.tlen
            pos += th.headerlen()
            while pos < tend:
                h = self._read_data_header(pos)
                if index.get(h.oid) != pos:
                    pos += h.recordlen()
                    continue

                pos += h.recordlen()

                # If we are going to copy any data, we need to copy
                # the transaction header.  Note that we will need to
                # patch up the transaction length when we are done.
                if not new_tpos:
                    th.status = "p"
                    new_tpos = output.tell()
                    output.write(th.asString())

                if h.plen:
                    data = self._file.read(h.plen)
                else:
                    # If a current record has a backpointer, fetch
                    # refs and data from the backpointer.  We need
                    # to write the data in the new record.
                    data = self.fetchBackpointer(h.oid, h.back) or ''

                h.prev = 0
                h.back = 0
                h.plen = len(data)
                h.tloc = new_tpos
                new_index[h.oid] = output.tell()
                output.write(h.asString())
                output.write(data)
                if not data:
                    # Packed records never have backpointers (?).
                    # If there is no data, write a z64 backpointer.
                    # This is a George Bailey event.
                    output.write(z64)

            if new_tpos:
                new_pos = output.tell()
                tlen = p64(new_pos - new_tpos)
                output.write(tlen)
                new_pos += 8

                if tlen != th.tlen:
                    # Update the transaction length
                    output.seek(new_tpos + 8)
                    output.write(tlen)
                    output.seek(new_pos)

                output._freecache(new_pos)


            pos += 8

        return new_index, new_pos

    def copyFromPacktime(self, input_pos, file_end, output, index):
        while input_pos < file_end:
            input_pos = self._copyNewTrans(input_pos, output, index)
            output._freecache(output.tell())
        return input_pos


def _freefunc(f):
    # Return an posix_fadvise-based cache freeer.

    try:
        import _zc_FileStorage_posix_fadvise
    except ImportError:
        return lambda pos: None

    fd = f.fileno()
    last = [0]
    def _free(pos):
        if pos == 4:
            last[0] = 0
        elif (pos - last[0]) < 50000000:
            return

        last[0] = pos
        _zc_FileStorage_posix_fadvise.advise(
            fd, 0, last[0]-10000,
            _zc_FileStorage_posix_fadvise.POSIX_FADV_DONTNEED)

    return _free
