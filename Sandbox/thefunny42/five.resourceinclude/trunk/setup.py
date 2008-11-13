from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='five.resourceinclude',
      version=version,
      description="z3c.resourceinclude support for Zope 2",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?:action=list_classifiers
      classifiers=[
          "Environment :: Web Environment",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: Zope Public License",
          "Programming Language :: Python",
          "Topic :: Software Development :: Libraries :: Python Modules",
          "Framework :: Zope2",
          ],
      keywords='zope2 resourceinclude z3c',
      author='Sylvain Viollon',
      author_email='zope-dev@zope.org',
      url='http://svn.zope.org/five.resourceinclude/',
      license='ZPL',
      packages=find_packages('src', exclude=['ez_setup']),
      package_dir={'': 'src'},
      namespace_packages=['five'],
      include_package_data=True,
      zip_safe=False,	
      install_requires=[
          'setuptools',
          'z3c.resourceinclude',
      ],
      entry_points="""
      """,
      )
