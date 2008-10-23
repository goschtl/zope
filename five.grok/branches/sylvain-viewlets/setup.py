from setuptools import setup, find_packages
import os

version = '1.0dev'

setup(name='five.grok',
      version=version,
      description="Grok-like layer for Zope 2",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
          "Environment :: Web Environment",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: Zope Public License",
          "Programming Language :: Python",
          "Topic :: Software Development :: Libraries :: Python Modules",
          "Framework :: Zope2",
          ],
      keywords='zope2 grok',
      author='Lennart Regebro, Godefroid Chapelle',
      author_email='grok-dev@zope.org',
      url='http://svn.zope.org/five.grok/',
      license='ZPL',
      packages=find_packages('src', exclude=['ez_setup']),
      package_dir={'': 'src'},
      namespace_packages=['five'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'martian',
          'grokcore.security',
          'grokcore.view >= 1.1',
          'grokcore.formlib',
          'grokcore.viewlet',
      ],
      entry_points="""
      """,
      )
