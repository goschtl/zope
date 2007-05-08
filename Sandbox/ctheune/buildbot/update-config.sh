#!/bin/bash
# update-cruise.sh -- created 04-Mai-2007, <+NAME+>
# @Last Change: 24-Dez-2004.
# @Revision:    0.0

HOME=/home/ctheune/buildbot/master
BASE=svn://svn.zope.org/repos/main/

cd $HOME
rm -f project-updates
for PROJECT in `svn ls $BASE`; do
    svn ls $BASE/$PROJECT/trunk/buildout.cfg 2> /dev/null
    if [ "$?" != "0" ]; then
        continue; 
    fi
    echo $PROJECT >> project-updates
done
# Remove trailing slashes
cat project-updates | sed "s/\/*$//" > projects

# Restart the master
buildbot restart .

# vi: 
