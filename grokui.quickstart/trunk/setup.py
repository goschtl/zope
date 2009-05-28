from setuptools import setup, find_packages
import sys, os

version = '0.1dev'

long_description = (open('README.txt').read() +
                    '\n\n' +
                    open('CHANGES.txt').read())


setup(name='grokui.quickstart',
      version=version,
      description="A Grok default view for the ZODB root folder",
      long_description=long_description,
      classifiers=['Development Status :: 3 - Alpha',
                   'Environment :: Web Environment',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: Zope Public License',
                   'Programming Language :: Python',
                   'Operating System :: OS Independent',
                   'Topic :: Internet :: WWW/HTTP',
                   ], 
      keywords='grok',
      author='Michael Haubenwallner',
      author_email="grok-dev@zope.org",
      url="http://svn.zope.org/grokui.quickstart",
      license='ZPL',
      package_dir={'': 'src'},
      packages=find_packages('src'),
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'grok',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )

