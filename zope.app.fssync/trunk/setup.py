import os

from setuptools import setup, find_packages, Extension

setup(name='zope.app.fssync',
      version='3.4dev',
      url='http://svn.zope.org/zope.app.fssync',
      license='ZPL 2.1',
      description='Zope container',
      author='Zope Corporation and Contributors',
      
	  packages=find_packages('src'),
      package_dir = {'': 'src'},

      namespace_packages=['zope', 'zope.app'],
      include_package_data = True,

      zip_safe = False,
      )
