# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from os.path import join

version = '0.6dev'
HISTORY = open(join("docs", "HISTORY.txt")).read()
README = open(join("src", "megrok", "resource", "README.txt")).read()

test_requires = [
    'zope.app.testing',
    'zope.app.zcmlfiles',
    'zope.publisher',
    'zope.securitypolicy',
    'zope.testbrowser',
    'zope.testing',
    ]

setup(name='megrok.resource',
      version=version,
      description="Grok Resources based on hurry.resource",
      long_description="%s\n%s" % (README, HISTORY),
      keywords='Grok Resources',
      author='Souheil Chelfouh',
      author_email='trollfot@gmail.com',
      url='http://pypi.python.org/pypi/megrok.resource',
      license='ZPL 2.1',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['megrok'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'martian',
          'setuptools',
          'grokcore.component',
          'grokcore.view',
          'hurry.resource >= 0.4.1',
          'hurry.zoperesource >= 0.5',
          'z3c.hashedresource',
          'zope.site',
          'zope.app.publication',
          'zope.component',
          'zope.interface',
          'zope.security',
          'zope.traversing'
      ],
      extras_require={'test': test_requires},
      classifiers=[
          "Programming Language :: Python",
          "Topic :: Software Development :: Libraries :: Python Modules",
          "License :: OSI Approved :: Zope Public License",
          ],
      )
