#!/usr/local/bin/python1.5.2

import sys, os



def commit_hook(rpath, files):
    print 'committing in repository: %s' % rpath
    print 'files: %s' % `files`

    sys.exit(0)


if __name__=='__main__':
    if len(sys.argv) < 3:
        print 'not enough arguments'
        sys.exit(1)
    rpath=sys.argv[1]
    files=sys.argv[2:]
    commit_hook(rpath, files)
