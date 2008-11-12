from setuptools import setup, find_packages
import sys, os

version = '0.3'

setup(name='z3c.pt.compat',
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
      namespace_packages=['z3c', 'z3c.pt'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          ],
      extras_require = dict(
        zpt = ['zope.app.pagetemplate', 'zope.tal'],
        z3cpt = ['z3c.pt'],
        ), 
      tests_require = [
          'z3c.pt',
          'zope.tal',
          'zope.viewlet',
          'zope.app.publisher',
          'zope.app.pagetemplate',
          ],
      test_suite="z3c.pt.compat.tests.test_doctests.test_suite",
      )
