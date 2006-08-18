import os, sys

def do(command, errors=None):
    print 'DOING:', command
    if os.system(command):
        if errors is None:
            sys.exit(1)
        else:
            errors.append(command)

def chdir(d):
    print 'CHDIR', d
    os.chdir(d)


errors = []
do('rm -rf Zope-0.0.0*')
do('../../zpkgtools/bin/zpkg -caCZope.cfg Zope')
do('tar xzf Zope-0.0.0.tgz')
chdir('Zope-0.0.0')
do('./configure --prefix `pwd`/z --with-python=%s' % sys.executable)
do('make install')
chdir('z')
do("bin/zopetest -m. --all", errors)
do("bin/mkzopeinstance -d`pwd`/../i -uadmin:123 -m SHA1")
chdir('../i')
do("bin/test --testzope --all", errors)

if errors:
    print 'Failed:'
    for c in errors:
        print c
