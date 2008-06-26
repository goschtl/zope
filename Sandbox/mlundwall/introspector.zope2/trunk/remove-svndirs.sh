#!/bin/bash
#This is just a script to remove the .svn directories.

if [ ! -e ./remove-svndirs.sh ] ; then
    echo "This script must be run from the same directory as it exists in."
    exit 1
    fi

find . -name ".svn" -type d -exec echo "removing:" {} \; -exec rm -rf {} \;

echo "All done. It's a good idea to remove this script now."
exit 0