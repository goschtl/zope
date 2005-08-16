
import os, sys

def do(command):
    print command
    if os.system(command):
        sys.exit(1)


do('rm -rf Zope-0.0.0*')
do('../../zpkgtools/bin/zpkg -caCZope.cfg Zope')
do('tar xozf Zope-0.0.0.tgz')
os.chdir('Zope-0.0.0')
do('./configure --prefix `pwd`/z')
do('make install')
os.chdir('z')
do("bin/zopetest '!(ZEO|ZODB|BTrees)'")
do("bin/mkzopeinstance -d`pwd`/../i -uadmin:123")
os.chdir('../i')
do("bin/test")


