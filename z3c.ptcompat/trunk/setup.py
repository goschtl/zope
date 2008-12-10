from setuptools import setup, find_packages
import sys, os

version = '0.3'

tests_require = ['z3c.pt',
                 'zope.tal',
                 'zope.viewlet',
                 'zope.app.publisher',
                 'zope.app.pagetemplate',
                 ],

setup(name='z3c.ptcompat',
      version=version,
      description="Compatibility-layer for Zope Page Template engines.",
      long_description=open('README.txt').read(),
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='zpt',
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',
      url='',
      license='ZPL',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['z3c'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          ],
      extras_require = dict(
        zpt = ['zope.app.pagetemplate', 'zope.tal'],
        z3cpt = ['z3c.pt'],
        test = tests_require, # used by buildout.cfg testrunner
        ), 
      tests_require = tests_require,
      test_suite="z3c.ptcompat.tests.test_doctests.test_suite",
      )
