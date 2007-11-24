from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='z3c.discriminator',
      version=version,
      description="Provides a formalism for using adapters with discriminators.",
      long_description="""\
This package provides a formalism for designating adapter arguments as
discriminators in the sense that they will be used only for adapter lookup,
not instantiation.""",
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
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
