#The script previously known as Jorgen the cleaner. Fixes inconsistent newlines before checkin.

if [ ! -e $1 ]; then
    if [ "$1"=="" ]; then 
        echo "Usage: newlinesfix.sh <filename>"
        echo "The old file will be saved as <filename>.old"
        exit 1
    fi
fi


cp $1 $1".old"
if [ ! -e $1".old" ] ; then
    echo "Failed to make backup copy of old file. Exiting..."
    exit 1
fi
    

cat $1".old" | perl -n -e "s/\r/\n/g;print" > $1

echo "All done. Happyness and all that."