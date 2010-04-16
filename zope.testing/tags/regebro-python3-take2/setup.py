##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
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
# This package is developed by the Zope Toolkit project, documented here:
# http://docs.zope.org/zopetoolkit
# When developing and releasing this package, please follow the documented
# Zope Toolkit policies as described by this documentation.
##############################################################################
"""Setup for zope.testing package

$Id$
"""

import os

try:
    from setuptools import setup
    extra = dict(
        namespace_packages=['zope',],
        install_requires = ['setuptools',
                            'zope.exceptions',
                            'zope.interface'],
        entry_points = {
            'console_scripts':
                ['zope-testrunner = zope.testing.testrunner:run',]},
        include_package_data = True,
        zip_safe = False,
        )
except ImportError:
    from distutils.core import setup
    extra = {}

import sys
if sys.version_info >= (3,):
    # Python 3 support:
    extra['use_2to3'] = True
    extra['setup_requires'] = ['zope.fixers']
    extra['use_2to3_fixers'] = ['zope.fixers']
    # These are only needed until zope.interface and zope.exceptions are
    # released with Python 3 support. Copy the pre-releases into the local
    # directory before you run setup.py under Python 3:
    extra['install_requires'] = ['setuptools',
                                 'zope.exceptions >= 3.6.0dev',
                                 'zope.interface >= 3.6.0dev']
    extra['convert_2to3_doctests'] = [
        'src/zope/testing/doctests.txt',
        'src/zope/testing/formparser.txt',
        'src/zope/testing/module.txt',
        'src/zope/testing/setupstack.txt',
        'src/zope/testing/testrunner/testrunner-arguments.txt',
        'src/zope/testing/testrunner/testrunner-coverage-win32.txt',
        'src/zope/testing/testrunner/testrunner-coverage.txt',
        'src/zope/testing/testrunner/testrunner-debugging-layer-setup.test',
        'src/zope/testing/testrunner/testrunner-debugging.txt',
        'src/zope/testing/testrunner/testrunner-discovery',
        'src/zope/testing/testrunner/testrunner-edge-cases.txt',
        'src/zope/testing/testrunner/testrunner-errors.txt',
        'src/zope/testing/testrunner/testrunner-gc.txt',
        'src/zope/testing/testrunner/testrunner-knit.txt',
        'src/zope/testing/testrunner/testrunner-layers-api.txt',
        'src/zope/testing/testrunner/testrunner-layers-buff.txt',
        'src/zope/testing/testrunner/testrunner-layers-ntd.txt',
        'src/zope/testing/testrunner/testrunner-layers.txt',
        'src/zope/testing/testrunner/testrunner-leaks-err.txt',
        'src/zope/testing/testrunner/testrunner-leaks.txt',
        'src/zope/testing/testrunner/testrunner-profiling-cprofiler.txt',
        'src/zope/testing/testrunner/testrunner-profiling.txt',
        'src/zope/testing/testrunner/testrunner-progress.txt',
        'src/zope/testing/testrunner/testrunner-repeat.txt',
        'src/zope/testing/testrunner/testrunner-simple.txt',
        'src/zope/testing/testrunner/testrunner-tb-format.txt',
        'src/zope/testing/testrunner/testrunner-test-selection.txt',
        'src/zope/testing/testrunner/testrunner-verbose.txt',
        'src/zope/testing/testrunner/testrunner-wo-source.txt',
        'src/zope/testing/testrunner/testrunner.txt',
        'src/zope/testing/testrunner/testrunner-ex/sampletests.txt',
        'src/zope/testing/testrunner/testrunner-ex/sampletestsl.txt',
        'src/zope/testing/testrunner/testrunner-ex/unicode.txt',
        ]
    extra['dependency_links'] = ['.']

from setuptools.command.test import test

class custom_test(test):
    # The zope.testing tests MUST be run using it's own testrunner. This is
    # because it's subprocess testing will call the script it was run with. We
    # therefore create a script to run the testrunner, and call that.
    def run(self):
        if self.distribution.install_requires:
            self.distribution.fetch_build_eggs(self.distribution.install_requires)
        if self.distribution.tests_require:
            self.distribution.fetch_build_eggs(self.distribution.tests_require)
        self.with_project_on_sys_path(self.run_tests)

    def run_tests(self):
        template = """
import sys
sys.path = %s

import os
os.chdir('%s')

import zope.testing.testrunner
if __name__ == '__main__':
    zope.testing.testrunner.run([
        '--test-path', '%s',
        ])
        """
        import tempfile
        fd, filename = tempfile.mkstemp(prefix='temprunner', text=True)
        scriptfile = open(filename, 'w')
        script = template % (sys.path, os.path.abspath(os.curdir), os.path.abspath('src'))
        scriptfile.write(script)
        scriptfile.close()
 
        import subprocess
        process = subprocess.Popen([sys.executable, filename])
        process.wait()
        os.unlink(filename)
    
    
chapters = '\n'.join([
    open(os.path.join('src', 'zope', 'testing', 'testrunner', name)).read()
    for name in (
        'testrunner.txt',
        'testrunner-simple.txt',
        'testrunner-layers-api.txt',
        'testrunner-layers.txt',
        'testrunner-arguments.txt',
        'testrunner-verbose.txt',
        'testrunner-test-selection.txt',
        'testrunner-progress.txt',

        # The following seems to cause weird unicode in the output: :(
        ##     'testrunner-errors.txt',

        'testrunner-debugging.txt',
        'testrunner-layers-ntd.txt',
        'testrunner-coverage.txt',
        'testrunner-profiling.txt',
        'testrunner-wo-source.txt',
        'testrunner-repeat.txt',
        'testrunner-gc.txt',
        'testrunner-leaks.txt',
        'testrunner-knit.txt',
    )])

chapters += '\n'.join([
    open(os.path.join('src', 'zope', 'testing', name)).read()
    for name in (
        'formparser.txt',
        'setupstack.txt',
    )])

long_description=(
    open('README.txt').read()
    + '\n' +
    open('CHANGES.txt').read()
    + '\n' +
    'Detailed Documentation\n'
    '**********************\n'
    + '\n' + chapters
    )

setup(
    name='zope.testing',
    version = '3.10.0dev',
    url='http://pypi.python.org/pypi/zope.testing',
    license='ZPL 2.1',
    description='Zope testing framework, including the testrunner script.',
    long_description=long_description,
    author='Zope Foundation and Contributors',
    author_email='zope-dev@zope.org',

    packages=["zope", "zope.testing", "zope.testing.testrunner",
              "zope.testing.testrunner.testrunner-ex",
              "zope.testing.testrunner.testrunner-ex-251759",
              "zope.testing.testrunner.testrunner-ex-pp-lib",
              "zope.testing.testrunner.testrunner-ex-pp-products",
              ],
    package_dir = {'': 'src'},

    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Framework :: Zope3",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Zope Public License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.4",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Testing",
        ],
    cmdclass = {'test': custom_test},
    **extra)
