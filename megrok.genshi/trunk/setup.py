from setuptools import setup, find_packages

version = '0.9'

setup(name='megrok.genshi',
      version=version,
      description="Genshi integration in Grok",
      long_description="""\
Support for using the Genshi templating language in the Grok web application
framework. See http://genshi.edgewall.org/ and http://grok.zope.org/
""",
      # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=['Development Status :: 3 - Alpha',
                   'Framework :: Zope3',
                   'License :: OSI Approved :: Zope Public License',
                   'Operating System :: OS Independent',
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
                        'Genshi',
                        ],
      entry_points="""
      # Add entry points here
      """,
      )
