##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""Read and (re-)format BoboPOS 2 database files
"""

import struct, string, sys, time, os

try: from cStringIO import StringIO
except: from StringIO import StringIO

ppml=None

file__version__=3.0
packed_version='SDBMV'+struct.pack(">f",file__version__)

def error(message, fatal=0, exc=0):
    if exc:
        sys.stderr.write('%s: %s' % (sys.exc_info()[0], sys.exc_info()[1]))
    sys.stderr.write("\n%s\n" % message)
    if fatal: sys.exit(fatal)

def _read_and_report(file, rpt=None, fromEnd=0, both=0, n=99999999, show=0,
                     forgive=0, export=0):
    """\
    Read a file's index up to the given time.
    """
    first=1
    seek=file.seek
    read=file.read
    unpack=struct.unpack
    split=string.split
    join=string.join
    find=string.find
    seek(0,2)
    file_size=file.tell()
    if not export:
        seek(0)
        h=read(len(packed_version))
        if h != packed_version:
            if h[:4]=='FS21':
                error("The input file is a ZODB File Storage\n"
                      "This script only works with ZODB 2 (BoboPOS) "
                      "data or export files."
                      ,1)
            else:
                error("The input file is not a ZODB 2 database file.\n"
                      "This script only works with ZODB 2 (BoboPOS) "
                      "data or export files."
                      ,1)

    gmtime=time.gmtime

    if fromEnd: pos=file_size
    else:       pos=newpos=(not export) and len(packed_version)

    tlast=0
    err=0
    tnamelast=None
    while 1:
        if fromEnd:
            seek(pos-4)
            l=unpack(">i", read(4))[0]
            if l==0:
                b=pos
                p=pos-4
                while l==0:
                    p=p-4
                    seek(p)
                    l=unpack(">i", read(4))[0]

                pos=p+4
                error("nulls skipped from %s to %s" % (pos,b))
            p=pos-l
            if p < 0:
                error('Corrupted data before %s' % pos)
                if show > 0:
                    p=pos-show
                    if p < 0: p=0
                    seek(p)
                    p=read(pos-p)
                else:
                    p=''
                error(p,1)
            pos=p
        else:
            pos=newpos

        seek(pos)
        h=read(24) # 24=header_size
        if not h: break
        if len(h) !=  24: break
        oid,prev,start,tlen,plen=unpack(">iidii",h)

        if prev < 0 or (prev and (prev >= pos)):
            error('Bad previous record pointer (%s) at %s' % (prev, pos))
            if show > 0: error(read(show))
            if not forgive:
                err=1
                break

        if start < tlast:
            error('record time stamps are not chronological at %s' % pos)
            if show > 0: error(read(show))
            if not forgive:
                err=1
                break

        if plen > tlen or plen < 0 or oid < -999:
            error('Corrupted data record at %s' % pos)
            if show > 0: error(read(show))
            err=1
            break


        newpos=pos+tlen
        if newpos > file_size:
            error('Truncated data record at %s' % pos)
            if show > 0: error(read(show))
            if not forgive:
                err=1
                break

        seek(newpos-4)
        if read(4) != h[16:20]:
            __traceback_info__=pos, oid,prev,start,tlen,plen
            error('Corrupted data record at %s' % pos)
            if show > 0:
                seek(pos+24)
                error(read(show))
            err=1
            break

        tlast=start-100

        if rpt is None: continue
        n=n-1
        if n < 1: break

        seek(pos+24)
        if plen > 0:
            p=read(plen)
            if p[-1:] != '.':
                error('Corrupted pickle at %s %s %s' % (pos,plen,len(p)))
                if show > 0:
                    seek(pos+24)
                    error(read(show))
                err=1
                break

        else: p=''
        t=split(read(tlen-plen-28),'\t')
        tname, user = (t+[''])[:2]
        t=join(t[2:],'\t')
        start,f=divmod(start,1)
        y,m,d,h,mn,s=gmtime(start)[:6]
        s=s+f
        start="%.4d-%.2d-%.2d %.2d:%.2d:%.3f" % (y,m,d,h,mn,s)
        rpt(pos,oid,start,tname,user,t,p,first,tname!=tnamelast)
        first=0
        tnamelast=tname

    if err and both and not fromEnd:
        _read_and_report(file, rpt, 1, 0, n, show)

    rpt(None, None, None, None, None, None, None, None, None)


def none(*ignored): pass

def positions(pos, *ignored):
    if pos is not None: sys.stdout.write("%s\n" % pos)

def oids(pos, oid, *ignored):
    if pos is not None: sys.stdout.write("%s\n" % oid)

def tab_delimited(*args):
    sys.stdout.write("%s\n" % string.join(args[:6],'\t'))

def undo_log(pos, oid, start, tname, user, t, p, first, newtrans):
    if not newtrans: return

    sys.stdout.write("%s:\t%s\t%s\t%s\n" % (pos, start, user, t))


reports={
    'none': (none,
             ('Read a database file checking for errors',
              'but producing no output')
             ),
    'oids': (oids,
             ('Read the database and output object ids',)),
    'positions': (positions,
                  ('Read the database and output record positions',)),
    'tab_delimited': (tab_delimited,
                      ('Output record meta-data in tab-delimited format',)),

    'undo': (undo_log,
             (
                 'Output a transaction summary that shows the position of',
                 'each transaction.  This is useful for undoing ',
                 'transactions from the OS command line when',
                 'some programming error has caused objects to get to',
                 'a state where Zope can\'t start up.',
                 '',
                 'Eventually, there will be an undo utility for undoing',
                 'individual transactions.  For now, you can simply',
                 'truncate the file at the position of a problem',
                 'transaction to return the database to the state it',
                 'was in before the transaction',
                 )),
    }

def main(argv):
    import getopt

    items=reports.items()
    items.sort()

    usage="""Usage: python %s [options] filename

    where filename is the name of the database file.

    options:

       -r report

          Specify an output report.

          The valid reports are:\n\n\t\t%s

       -e

          Read the file from back to front

       -l n

          Show only n records

       -b

          If an error is encountered while reading from front,
          ret reading from the back.

       -s n

          If a corrupted data record is found, show the first n
          bytes of the corrupted record.

       -f filename

          Convert to ZODB 3 File-Storage format

       -p path

          Add a directory to the Python path.

       -x

          The input file is a ZODB 2 export file.


    """ % (sys.argv[0],
           string.join(map(
               lambda i:
               ("%s --\n\t\t\t%s" % (i[0], string.join(i[1][1],'\n\t\t\t'))),
               items),
               ',\n\n\t\t'))

    sys.path.append(os.path.split(sys.argv[0])[0])

    try:
        opts, args = getopt.getopt(argv,'r:ebl:s:f:p:x')
        filename,=args
    except: error(usage,1,1)

    try: file=open(filename,'rb')
    except: error('Coud not open %s' % filename,1,1)

    rpt=none
    fromEnd=0
    both=0
    n=99999999
    show=0
    export=0
    convert=0
    for o, v in opts:
        o=o[1:]
        if o=='r':
            try: rpt=reports[v][0]
            except: error('Invalid report: %s' % v, 1)
        elif o=='l':
            try: n=string.atoi(v)
            except: error('The number of records, %s, shuld ne an integer'
                          % v, 1)
        elif o=='s':
            try: show=string.atoi(v)
            except: error('The number of bytes, %s, shuld ne an integer'
                          % v, 1)
        elif o=='e': fromEnd=1
        elif o=='x': export=1
        elif o=='f': convert=1
        elif o=='b': both=1
        elif o=='p':
            if v=='-':
                v=os.path.join(
                    os.path.split(sys.argv[0])[0],
                    '..','lib','python')
            sys.path.insert(0,v)
            print sys.path
        else: error('Unrecognized option: -%s' % o, 1)

    if convert:
        import FS
        if export:
            rpt=FS.ZEXP(v, file).rpt
        else:
            rpt=FS.FS(v, file).rpt

    _read_and_report(file, rpt, fromEnd, both, n, show,
                     forgive=1, export=export)

if __name__=='__main__': main(sys.argv[1:])
