#! /bin/sh
# This script should be run to fix the references 
for x in *.css; do 
    sed 's|(\([a-z2]*\.gif\))|(/@@/megrok.datetimewidget/\1)|g' $x > tmp 
    mv tmp $x
done
