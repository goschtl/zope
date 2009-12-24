# -*- coding: utf-8 -*-

from os.path import join
from setuptools import setup, find_packages

version = '0.1'
name = 'megrok.resourceviewlet'

history = open(join('docs', 'HISTORY.txt')).read()
readme = open(join('src', 'megrok', 'resourceviewlet', 'README.txt')).read()

test_requires = [
    'grokcore.view',
    'zope.app.testing',
    'zope.app.zcmlfiles',
    'zope.contentprovider',
    'zope.testbrowser',
    'zope.testing',
    ]

setup(name=name,
      version=version,
      description='Grok component to include resources.',
      long_description=readme + '\n\n' + history,
      keywords='Grok Zope3 CMS Resources',
      author='Souheil Chelfouh',
      author_email='trollfot@gmail.com',
      url='http://tracker.trollfot.org/',
      download_url='',
      license='GPL',
      packages=find_packages('src', exclude=['ez_setup']),
      package_dir={'': 'src'},
      namespace_packages=['megrok'],
      include_package_data=True,
      platforms='Any',
      zip_safe=False,
      install_requires=[
          'hurry.resource',
          'grokcore.viewlet',
          'megrok.resource',
          'setuptools',
          'zope.schema',
          'zope.interface',
          'zope.viewlet',
          ],
      extras_require={'test': test_requires},
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Web Environment',
          'Framework :: Zope3',
          'Intended Audience :: Other Audience',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          ],
      )
