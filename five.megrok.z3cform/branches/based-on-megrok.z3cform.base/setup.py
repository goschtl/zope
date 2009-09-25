from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='five.megrok.z3cform',
      version=version,
      description="Z3C From support for five.grok",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          "Environment :: Web Environment",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: Zope Public License",
          "Programming Language :: Python",
          "Topic :: Software Development :: Libraries :: Python Modules",
          "Framework :: Zope2",
        ],
      keywords='z3c form five grok',
      author='Sylvain Viollon',
      author_email='grok-dev@zope.org',
      url='http://svn.zope.org/five.megrok.z3cform/trunk',
      license='ZPL',
      packages=find_packages('src', exclude=['ez_setup']),
      package_dir={'': 'src'},
      namespace_packages=['five', 'five.megrok'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'five.grok',
          'megrok.z3cform',
          'plone.z3cform'
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
