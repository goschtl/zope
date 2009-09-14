from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='megrok.z3cform.wizard',
      version=version,
      description="grok add on for createing an Wizard",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='grok z3c.form megrok.z3cform.wizard',
      author='Christian Klinger',
      author_email='cklinger@novareto.de',
      url='',
      license='GPL',
      package_dir={'':'src'},
      packages=find_packages('src', exclude=['ez_setup']),
      namespace_packages=['megrok', 'megrok.z3cform'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
	  'z3c.wizard',
          'grok',
	  'megrok.z3cform.base',
          'megrok.pagetemplate',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
