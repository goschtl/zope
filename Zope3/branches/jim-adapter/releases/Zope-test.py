import os, sys

def do(command):
    print command
    if os.system(command):
        sys.exit(1)


do('rm -rf Zope-0.0.0*')
do('../../zpkgtools/bin/zpkg -caCZope.cfg Zope')
do('tar xozf Zope-0.0.0.tgz')
os.chdir('Zope-0.0.0')
do('./configure --prefix `pwd`/z --with-python=%s' %sys.executable)
do('make install')
os.chdir('z')
do("bin/zopetest -vp '!(ZEO|ZODB|BTrees)'")
do("bin/mkzopeinstance -d`pwd`/../i -uadmin:123 -m SHA1")
os.chdir('../i')
do("bin/test --testzope -vp")
