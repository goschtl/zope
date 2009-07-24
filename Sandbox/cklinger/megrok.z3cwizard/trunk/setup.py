from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='megrok.z3cwizard',
      version=version,
      description="grok add on for createing an Wizard",
      long_description=open("README.txt").read() + "\n" +
                       open("HISTORY.txt").read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='grok z3c.form megrok.z3cform wizard',
      author='Christian Klinger',
      author_email='cklinger@novareto.de',
      url='',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['megrok'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
	  'z3c.wizard',
	  'megrok.z3cform',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
