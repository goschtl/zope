from setuptools import setup, find_packages
import sys, os

setup(name='z3c.vcsync',
      version='0.1',
      description="Sync ZODB data with version control system, currently SVN",
      package_dir={'': 'src'},
      packages=find_packages('src'),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'setuptools',
        'grok',
        'py',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
