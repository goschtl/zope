from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='megrok.z3cform',
      version=version,
      description="Z3C Forms support for Grok",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          "Environment :: Web Environment",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: Zope Public License",
          "Programming Language :: Python",
          "Topic :: Software Development :: Libraries :: Python Modules",
          "Framework :: Zope3",
        ],
      keywords='z3c forms grok',
      author='Sylvain Viollon',
      author_email='grok-dev@zope.org',
      url='http://svn.zope.org/megrok.z3cform/trunk',
      license='ZPL',
      packages=find_packages('src', exclude=['ez_setup']),
      package_dir={'': 'src'},
      namespace_packages=['megrok'],
      include_package_data=True,
      zip_safe=False,
      # We need to factor out the dependency on grokcore.formlib
      install_requires=[
          'setuptools',
          'grokcore.component',
          'grokcore.view',
          'grokcore.formlib',
          'z3c.form'
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
