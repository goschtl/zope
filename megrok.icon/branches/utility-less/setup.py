# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from os.path import join

name = 'megrok.icon'
version = '0.1'
readme = open(join('src', 'megrok', 'icon', "README.txt")).read()
history = open(join('docs', 'HISTORY.txt')).read()


install_requires = [
    'grokcore.component',
    'grokcore.view',
    'martian',
    'setuptools',
    'zope.browserresource',
    'zope.component',
    'zope.container',
    'zope.interface',
    'zope.location',
    'zope.publisher',
    'zope.schema',
    'zope.security',
    'zope.site',
    'zope.traversing',
    ]

tests_require = [
    'zope.testing',
    'zope.testbrowser',
    'zope.app.testing',
    'zope.app.zcmlfiles',
    ]

setup(name = name,
      version = version,
      description = 'Icon registration utility',
      long_description = readme + '\n\n' + history,
      keywords = 'Grok Zope3 CMS Dolmen Icon',
      author = 'Souheil Chelfouh',
      author_email = 'trollfot@gmail.com',
      url = '',
      license = 'ZPL 2.1',
      packages=find_packages('src', exclude=['ez_setup']),
      package_dir={'': 'src'},
      namespace_packages = ['megrok'],
      include_package_data = True,
      platforms = 'Any',
      zip_safe = False,
      tests_require = tests_require,
      install_requires = install_requires,
      extras_require = {'test': tests_require},
      classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Zope3',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        ],
      )
