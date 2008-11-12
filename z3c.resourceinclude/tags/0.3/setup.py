from setuptools import setup, find_packages
import sys, os

version = '0.3'

setup(name='z3c.resourceinclude',
      version=version,
      description="Machinery to include web resources based on request layer.",
      long_description=open('README.txt').read(),
      classifiers=[
        "Framework :: Zope2",
        "License :: OSI Approved :: Zope Public License",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Operating System :: OS Independent",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Malthe Borch',
      author_email='mborch@gmail.com',
      url='',
      license='ZPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['z3c'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'zope.app.publisher',
          'zope.app.cache',
          'zope.contentprovider',
          'plone.memoize',
          'z3c.pt',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
