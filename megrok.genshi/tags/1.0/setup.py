from setuptools import setup, find_packages

version = '1.0dev'

long_description = (open('README.txt').read() +
                    '\n\n' +
                    open('CHANGES.txt').read())

setup(name='megrok.genshi',
      version=version,
      description="Genshi integration in Grok",
      long_description=long_description,
      # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=['Development Status :: 3 - Alpha',
                   'Environment :: Web Environment',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: Zope Public License',
                   'Programming Language :: Python',
                   'Operating System :: OS Independent',
                   'Topic :: Internet :: WWW/HTTP',
                   ], 
      keywords="grok genshi",
      author="Lennart Regebro, Guido Wesdorp",
      author_email="regebro@gmail.com",
      url="http://svn.zope.org/megrok.genshi/",
      license="ZPL",
      package_dir={'': 'src'},
      packages=find_packages('src'),
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'grok',
                        'Genshi',
                        ],
      entry_points="""
      # Add entry points here
      """,
      )
