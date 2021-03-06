from setuptools import setup, find_packages
import os

version = '0.3.0'

setup(name='five.taskqueue',
      version=version,
      description="Zope2 integration of z3c.taskqueue",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='Godefroid Chapelle',
      author_email='gotcha@bubblenet.be',
      url='http://pypi.python.org/pypi/five.taskqueue',
      license='ZPL 2.1',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['five'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Zope2',
          'z3c.taskqueue >= 0.2.0',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
