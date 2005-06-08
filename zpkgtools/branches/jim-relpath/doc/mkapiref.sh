#! /bin/sh

# Script to drive Epydoc to generate API documentation.  This mostly
# just records the command line so it can be reused, and drops the
# documentation in the same place every time.

cd `dirname $0`
cd ..

if [ -e doc/apiref ] ; then
    if [ -e doc/apiref-backup ] ; then
        rm -r doc/apiref-backup/ || exit $?
    fi
    mv doc/apiref doc/apiref-backup || exit $?
fi

epydoc -o doc/apiref -n 'Zope Packaging Tools' --docformat restructuredtext \
    zpkgtools zpkgsetup

ERR=$?

if [ $ERR -eq 0 -a -d doc/apiref-backup ] ; then
    rm -r doc/apiref-backup || exit $?
fi

exit $ERR
