#!/usr/bin/env python

# repozo.py -- incremental and full backups of a Data.fs file.
#
# Originally written by Anthony Baxter
# Significantly modified by Barry Warsaw
#
# TODO:
#    allow gzipping of backup files.
#    allow backup files in subdirectories.

"""repozo.py -- incremental and full backups of a Data.fs file.

Usage: %(program)s [options]
Where:

    -B / --backup
        backup current ZODB file

    -R / --recover
        restore a ZODB file from a backup

    -v / --verbose
        Verbose mode

    -h / --help
        Print this text and exit

Flags for --backup and --recover:
    -r dir
    --repository=dir
        Repository directory containing the backup files

Flags for --backup:
    -f file
    --file=file
        Source Data.fs file

    -F / --full
        Force a full backup

Flags for --recover:
    -D str
    --date=str
        Recover state as at this date.  str is in the format
        yyyy-mm-dd[-hh[-mm]]

    -o file
    --output=file
        Write recovered ZODB to given file.  If not given, the file will be
        written to stdout.

One of --backup or --recover is required.
"""

from __future__ import nested_scopes

import os
import sys
import md5
import time
import getopt

from ZODB.FileStorage import FileStorage

program = sys.argv[0]

try:
    True, False
except NameError:
    True = 1
    False = 0

BACKUP = 1
RECOVER = 2

COMMASPACE = ', '
READCHUNK = 16 * 1024
VERBOSE = False



def usage(code, msg=''):
    outfp = sys.stderr
    if code == 0:
        outfp = sys.stdout

    print >> outfp, __doc__ % globals()
    if msg:
        print >> outfp, msg

    sys.exit(code)


def log(msg, *args):
    if VERBOSE:
        # Use stderr here so that -v flag works with -R and no -o
        print >> sys.stderr, msg % args



def parseargs():
    global VERBOSE
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'BRvhf:r:FD:o:',
                                   ['backup', 'recover', 'verbose', 'help',
                                    'file=', 'repository=', 'full', 'date=',
                                    'output='])
    except getopt.error, msg:
        usage(1, msg)

    class Options:
        mode = None
        file = None
        repository = None
        full = False
        date = None
        output = None

    options = Options()

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage(0)
        elif opt in ('-R', '--recover'):
            if options.mode is not None:
                usage(1, '-B and -R are mutually exclusive')
            options.mode = RECOVER
        elif opt in ('-B', '--backup'):
            if options.mode is not None:
                usage(1, '-B and -R are mutually exclusive')
            options.mode = BACKUP
        elif opt in ('-v', '--verbose'):
            VERBOSE = True
        elif opt in ('-f', '--file'):
            options.file = arg
        elif opt in ('-r', '--repository'):
            options.repository = arg
        elif opt in ('-F', '--full'):
            options.full = True
        elif opt in ('-D', '--date'):
            options.date = arg
        elif opt in ('-o', '--output'):
            options.output = arg

    # Any other arguments are invalid
    if args:
        usage(1, 'Invalid arguments: ' + COMMASPACE.join(args))

    # Sanity checks
    if options.mode is None:
        usage(1, 'Either --backup or --recover is required')
    if options.repository is None:
        usage(1, '--repository is required')
    if options.mode == BACKUP:
        if options.date is not None:
            log('--date option is ignored in backup mode')
            options.date = None
        if options.output is not None:
            log('--output option is ignored in backup mode')
            options.output = None
    else:
        assert options.mode == RECOVER
        if options.file is not None:
            log('--file option is ignored in recover mode')
            options.file = None
    return options



# Do something with a run of bytes from a file
def dofile(func, fp, n):
    bytesread = 0
    stop = False
    chunklen = READCHUNK
    while not stop:
        if chunklen + bytesread > n:
            chunklen = n - bytesread
            stop = True
        data = fp.read(chunklen)
        if not data:
            break
        func(data)
        bytesread += chunklen
    return bytesread


def checksum(filename, n):
    # Checksum the first n bytes of the specified file
    sum = md5.new()
    fp = open(filename, 'rb')
    def func(data):
        sum.update(data)
    dofile(func, fp, n)
    return sum.hexdigest()


def copyfile(src, dst, start, n):
    # Copy bytes from file src, to file dst, starting at offset start, for n
    # length of bytes
    ifp = open(src, 'rb')
    ifp.seek(start)
    ofp = open(dst, 'wb')
    def func(data):
        ofp.write(data)
    dofile(func, ifp, n)
    ofp.close()
    ifp.close()


def concat(files, ofp=None):
    # Concatenate a bunch of files from the repository, output to `outfile' if
    # given.  Return the number of bytes written and the md5 checksum of the
    # bytes.
    sum = md5.new()
    def func(data):
        sum.update(data)
        if ofp:
            ofp.write(data)
    bytesread = 0
    for f in files:
        ifp = open(f, 'rb')
        bytesread += dofile(func, ifp, os.path.getsize(f))
        ifp.close()
    if ofp:
        ofp.close()
    return bytesread, sum.hexdigest()


def gen_filename(options, ext=None):
    if ext is None:
        if options.full:
            ext = '.fs'
        else:
            ext = '.deltafs'
    t = time.gmtime()[:6] + (ext,)
    return '%04d-%02d-%02d-%02d-%02d-%02d%s' % t


def find_files(options):
    def rootcmp(x, y):
        # This already compares in reverse order
        return cmp(os.path.splitext(y)[0], os.path.splitext(x)[0])
    # Return a list of files needed to reproduce state at time `when'
    when = options.date
    if not when:
        when = gen_filename(options, '')
    log('looking for files b/w last full backup and %s...', when)
    all = os.listdir(options.repository)
    all.sort(rootcmp)
    # Find the last full backup before date, then include all the incrementals
    # between when and that full backup.
    needed = []
    for file in all:
        root, ext = os.path.splitext(file)
        if root <= when:
            needed.append(file)
        if ext == '.fs':
            break
    # Make the file names relative to the repository directory
    needed = [os.path.join(options.repository, f) for f in needed]
    # Restore back to chronological order
    needed.reverse()
    if needed:
        log('files needed to recover state as of %s:', when)
        for f in needed:
            log('\t%s', f)
    else:
        log('no files found')
    return needed



def do_full_backup(options):
    # Find the file position of the last completed transaction.
    fs = FileStorage(options.file, read_only=True)
    # Note that the FileStorage ctor calls read_index() which scans the file
    # and returns "the position just after the last valid transaction record".
    # getSize() then returns this position, which is exactly what we want,
    # because we only want to copy stuff from the beginning of the file to the
    # last valid transaction record.
    pos = fs.getSize()
    fs.close()
    options.full = True
    dest = os.path.join(options.repository, gen_filename(options))
    if os.path.exists(dest):
        print >> sys.stderr, 'Cannot overwrite existing file:', dest
        sys.exit(2)
    copyfile(options.file, dest, 0, pos)


def do_incremental_backup(options, dstfile, reposz):
    # Find the file position of the last completed transaction.
    fs = FileStorage(options.file, read_only=True)
    # Note that the FileStorage ctor calls read_index() which scans the file
    # and returns "the position just after the last valid transaction record".
    # getSize() then returns this position, which is exactly what we want,
    # because we only want to copy stuff from the beginning of the file to the
    # last valid transaction record.
    pos = fs.getSize()
    fs.close()
    options.full = False
    dest = os.path.join(options.repository, gen_filename(options))
    if os.path.exists(dest):
        print >> sys.stderr, 'Cannot overwrite existing file:', dest
        sys.exit(2)
    log('writing incremental: %s bytes to %s',  pos-reposz, dest)
    copyfile(options.file, dest, reposz, pos)


def do_backup(options):
    repofiles = find_files(options)
    # See if we need to do a full backup
    if options.full or not repofiles:
        log('doing a full backup')
        do_full_backup(options)
        return
    # See if we can do an incremental, based on the files that already exist.
    # This call of concat() will not write an output file.
    reposz, reposum = concat(repofiles)
    log('repository state: %s bytes, md5: %s', reposz, reposum)
    srcsz = os.path.getsize(options.file)
    # Get the md5 checksum of the source file, up to two file positions: the
    # entire size of the file, and up to the file position of the last
    # incremental backup.
    srcsum = checksum(options.file, srcsz)
    srcsum_backedup = checksum(options.file, reposz)
    log('current state   : %s bytes, md5: %s', srcsz, srcsum)
    log('backed up state : %s bytes, md5: %s', reposz, srcsum_backedup)
    # Has nothing changed?
    if srcsz == reposz and srcsum == reposum:
        log('No changes, nothing to do')
        return
    # Has the file shrunk (probably because of a pack)?
    if srcsz < reposz:
        log('file shrunk, possibly because of a pack (full backup)')
        do_full_backup(options)
        return
    # The source file is larger than the repository.  If the md5 checksums
    # match, then we know we can do an incremental backup.  If they don't,
    # then perhaps the file was packed at some point (or a non-transactional
    # undo was performed, but this is deprecated).  Only do a full backup if
    # forced to.
    #
    # XXX For ZODB4, this needs to take into account the storage metadata
    # header that FileStorage has grown at the front of the file.
    if reposum == srcsum_backedup:
        incrdest = gen_filename(options)
        do_incremental_backup(options, incrdest, reposz)
        return
    # The checksums don't match, meaning the front of the source file has
    # changed.  We'll need to do a full backup in that case.
    log('file changed, possibly because of a pack (full backup)')
    do_full_backup(options)



def do_recover(options):
    # Find the first full backup at or before the specified date
    repofiles = find_files(options)
    if not repofiles:
        if options.date:
            log('No files in repository before %s', options.date)
        else:
            log('No files in repository')
        return
    if options.output is None:
        log('Recovering file to stdout')
        outfp = sys.stdout
    else:
        log('Recovering file to %s', options.output)
        outfp = open(options.output, 'wb')
    reposz, reposum = concat(repofiles, outfp)
    if outfp <> sys.stdout:
        outfp.close()
    log('Recovered %s bytes, md5: %s', reposz, reposum)



def main():
    options = parseargs()
    if options.mode == BACKUP:
        do_backup(options)
    else:
        assert options.mode == RECOVER
        do_recover(options)


if __name__ == '__main__':
    main()
