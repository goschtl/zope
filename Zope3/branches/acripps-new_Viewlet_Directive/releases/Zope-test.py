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

if len(sys.argv) > 1:
    [version] = sys.argv[1:]
else:
    version = '0.0.0'


errors = []
do('rm -rf Zope-%s*' % version)
if version == '0.0.0':
    do('../../zpkgtools/bin/zpkg -caCZope.cfg Zope')
else:
    do('../../zpkgtools/bin/zpkg -caCZope.cfg -v %s -r %s Zope'
       % (version, version))
    
do('tar xzf Zope-%s.tgz' % version)
chdir('Zope-%s' % version)
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
