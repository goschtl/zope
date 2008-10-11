from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='five.clids',
      version=version,
      description="Zope2 adapters to plug into plone.clids",
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
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['five'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.clids',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
