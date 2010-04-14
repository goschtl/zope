##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Bootstrap the buildout project itself.

This is different from a normal boostrapping process because the
buildout egg itself is installed as a develop egg.

$Id: dev.py 103647 2009-09-08 16:03:44Z chrisw $
"""

import os, shutil, sys, subprocess
from urllib.request import urlopen

is_jython = sys.platform.startswith('java')

for d in 'eggs', 'develop-eggs', 'bin':
    if not os.path.exists(d):
        os.mkdir(d)

try:
    import pkg_resources
except ImportError:
    ez = {}
    exec(urlopen('http://python-distribute.org/distribute_setup.py').read(), ez)
    ez['use_setuptools'](to_dir='eggs', download_delay=0)

    import pkg_resources

subprocess.Popen(
    [sys.executable] +
    ['setup.py', '-q', 'build'],
    env = {'PYTHONPATH': os.path.dirname(pkg_resources.__file__)}).wait()
import pdb;pdb.set_trace()
#pkg_resources.working_set.add_entry('build/lib')
location = os.path.join(os.path.abspath( os.path.curdir), 'build', 'lib')
ws = pkg_resources.working_set
ws.entry_keys.setdefault('src', [])
ws.entries.append('src')
for dist in pkg_resources.find_distributions('src', True):
    dist.location = location
    ws.add(dist, 'src', False)

#sys.path.append(location)

import zc.buildout.easy_install
zc.buildout.easy_install.scripts(
    ['zc.buildout'], pkg_resources.working_set , sys.executable, 'bin')

bin_buildout = os.path.join('bin', 'buildout')

if is_jython:
    # Jython needs the script to be called twice via sys.executable
    assert subprocess.Popen([sys.executable] + [bin_buildout]).wait() == 0

sys.exit(subprocess.Popen(bin_buildout).wait())
