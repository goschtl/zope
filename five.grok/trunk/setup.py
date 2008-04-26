from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='five.grok',
      version=version,
      description="",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='',
      author_email='',
      url='',
      license='GPL',
      packages=find_packages('src', exclude=['ez_setup']),
      package_dir={'': 'src'},
      namespace_packages=['five'],
      include_package_data=True,
      zip_safe=False,	
      install_requires=[
          'setuptools',
          'grokcore.component',
      ],
      entry_points="""
      """,
      )
