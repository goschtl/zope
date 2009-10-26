from setuptools import setup, find_packages
import os
readme = open(os.path.join('src', 'megrok', 'z3cform', 'ui', 'README.txt')).read()

version = '0.3dev'
setup(name='megrok.z3cform.ui',
      version=version,
      description="Installation Helper for z3c.formui",
      long_description=readme + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='grok z3c.form megrok.z3cform.ui',
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
          'z3c.formui',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
