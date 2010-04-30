from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='zope.monkeypatches.doctest',
      version=version,
      description="Bugfixes for various bugs in the doctest module.",
      long_description=open(os.path.join("zope","monkeypatches", "doctest", "README.txt")).read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Zope Public License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.1",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Testing",
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
