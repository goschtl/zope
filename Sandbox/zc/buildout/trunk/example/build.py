#!/usr/bin/env python2.4
import sys, os

ENGINE_PATH = './buildout/engine'
ENGINE_URL = 'svn://svn.zope.org/repos/main/Sandbox/zc/buildout/trunk/src/engine'

# bootstrap the buildout code, if it doesn't yet exist
if os.path.exists(ENGINE_PATH):
    os.system('svn up %s' % ENGINE_PATH)
else:
    os.system('svn co %s %s ' % (ENGINE_URL, ENGINE_PATH))

sys.path.append(os.path.abspath(ENGINE_PATH))
sys.path.append(os.path.abspath('./buildout'))
from buildout import main
main(sys.argv)
