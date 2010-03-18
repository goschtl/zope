from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='megrok.z3cform.ajax',
      version=version,
      description="grok ajax libs",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: Zope Public License",
        ],
      keywords='grok z3c.form ajax jquery',
      author='Christian Klinger',
      author_email='cklinger@novareto.de',
      url='',
      license='ZPL',
      package_dir={'':'src'},
      packages=find_packages('src', exclude=['ez_setup']),
      namespace_packages=['megrok', 'megrok.z3cform'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'grok',
          'zope.app.testing',
          'zope.app.zcmlfiles',
	  'megrok.z3cform.base',
	  'megrok.z3cform.ui',
          'hurry.jquery',
          'megrok.resource',
          'zope.testbrowser',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
