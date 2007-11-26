from setuptools import setup, find_packages
import sys, os

version = '0.2'

setup(name='z3c.discriminator',
      version=version,
      description="Provides a formalism for marking adapter specifications as discriminators.",
      long_description=open("README.txt").read() + open("docs/HISTORY.txt").read(),
      classifiers=[
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='zope adapter discriminator',
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
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
