import os, sys

def do(command):
    print command
    if os.system(command):
        sys.exit(1)


do('rm -rf ZopeTestbrowser-0.0.0*')
do('../../zpkgtools/bin/zpkg -C ZopeTestbrowser.cfg')
do('tar xozf ZopeTestbrowser-0.0.0.tgz')
os.chdir('ZopeTestbrowser-0.0.0')
do('python setup.py install --home `pwd`/here')

zope3_path = os.path.abspath(os.curdir + '/../src')
tb_path = '.'#os.path.abspath(os.curdir + '/here/lib/python')
exp = 'export PYTHONPATH=%s:%s' %(zope3_path, tb_path)

os.chdir('here/lib/python')
tests_path = os.path.abspath(os.curdir + '/zope/testbrowser/ftests')
for fn in os.listdir(tests_path):
    if fn.startswith('test') and fn.endswith('.py'):
        do('%s; python %s/%s' %(exp, tests_path, fn))
