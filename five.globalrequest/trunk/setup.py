from setuptools import setup, find_packages
import os

version = '1.1dev'

setup(name='five.globalrequest',
      version=version,
      description="Zope 2 integration for zope.globalrequest",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='zope global request',
      author='Martin Aspeli',
      author_email='optilude@gmail.com',
      url='http://pypi.python.org/pypi/five.globalrequest',
      license='ZPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['five'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'zope.globalrequest',
          'Zope2',
      ],
      entry_points="""
      """,
      )
