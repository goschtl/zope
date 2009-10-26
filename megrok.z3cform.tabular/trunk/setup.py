from setuptools import setup, find_packages
import os

version = '0.2'
readme = open(os.path.join('src', 'megrok', 'z3cform', 'tabular', 'README.txt')).read()

setup(name='megrok.z3cform.tabular',
      version=version,
      description="Grok addon for createing tabular forms",
      long_description=readme + "\n" +
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
          'grok',
          'z3c.tabular',
          'megrok.layout',
          'megrok.z3cform.base',
          'megrok.z3cform.ui',
          'megrok.z3ctable',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
