from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='z3c.indexing.async',
      version=version,
      description="Asynchronous operation dispatching support.",
      long_description=open('README.txt').read(),
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',
      url='',
      license='ZPL',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['z3c', 'z3c.indexing'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'zope.interface',
          'zope.component',
          'zope.testing',
          'z3c.indexing.dispatch',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
