from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='zope.monkeypatches.doctest',
      version=version,
      description="Bugfixes for various bugs in the doctest module.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='doctest',
      author='Zope Foundation and Contributors',
      author_email='zope-dev@zope.org',
      url='http://pypi.python.org/pypi/zope.monkeypatches.doctest',
      license='ZPL 2.1',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['zope', 'zope.monkeypatches'],
      include_package_data=True,
      test_suite='zope.monkeypatches.doctest.test_suite',
      zip_safe=False,
      install_requires=[
          'setuptools',
      ],
      )
