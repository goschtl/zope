#!/bin/bash -x

HOME=$1
BASE=$2

cd $HOME
rm -f project-updates
for PROJECT in `svn ls $BASE`; do
    svn ls $BASE/$PROJECT/trunk/buildout.cfg &> /dev/null
    if [ "$?" != "0" ]; then
        continue;
    fi
    echo $PROJECT >> project-updates
done

# Remove trailing slashes
cat project-updates | sed "s/\/*$//" > project-list.cfg
rm -f project-updates

# Restart the master
make reconfig > /dev/null

# vi: