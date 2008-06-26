#!/bin/bash
#This is just a script to show what versions that need to be pinned in buildout.

if [ ! -e ./bin/buildout ] ; then
    echo "This script needs buildout to be in bin/buildout."
    exit 1
    fi

./bin/buildout -Novvvvv |sed -ne 's/^Picked: //p' | sort | uniq

#echo "All done. It's a good idea to remove this script now."
exit 0