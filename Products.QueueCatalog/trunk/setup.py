
import os
from setuptools import setup, find_packages


CLASSIFIERS = [
    'Programming Language :: Python',
    'Framework :: Zope2',
]


long_description = open(os.path.join('Products', 'QueueCatalog', 'README.txt')).read()
version = open(os.path.join('Products', 'QueueCatalog', 'version.txt')).read().strip()

setup(name='Products.QueueCatalog',
      version=version,
      license='ZPL (see LICENSE.txt)',
      author='Christian Theune',
      author_email='ct@gocept.com',
      maintainer='Christian Theune',
      maintainer_email='ct@gocept.com',
      classifiers=CLASSIFIERS,
      keywords='Zope2 Indexing Catalog Queue',
      url='http://www.zope.org/Members/ctheune/QueueCatalog',
      description='QueueCatalog - asynchronous cataloging',
      long_description=long_description,
      packages=['Products', 'Products.QueueCatalog'],
      include_package_data = True,
      zip_safe=False,
      install_requires=['setuptools'],
      namespace_packages=['Products'],

      )
