from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='grokcore.view',
      version=version,
      description="This package provides base classes for the Zope Views, "
        "as well as means for configuring and registering them directly "
        "in Python (without ZCML).",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='',
      author_email='',
      url='',
      license='ZPL',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['grokcore'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'martian',
          'grokcore.component',
          'zope.publisher',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
