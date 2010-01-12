from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='five.dbevent',
      version=version,
      description="Database startup events",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Godefroid Chapelle and Jean-Francois Roche',
      author_email='',
      url='http://pypi.python.org/pypi/five.dbevent',
      license='GPL',
      packages=find_packages('src', exclude=['ez_setup']),
      package_dir={'': 'src'},
      namespace_packages=['five'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'collective.monkeypatcher'],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
