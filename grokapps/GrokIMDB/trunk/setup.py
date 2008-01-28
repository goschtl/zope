from setuptools import setup, find_packages

version = '0.1'
long_description = (
    read('README.txt')
    + '\n\n'
    )

setup(name='GrokIMDB',
      version=version,
      description="A Grok demo application for editing data "
                  "retrieved from IMDb.",
      long_description=long_description,
      # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=['Development Status :: 3 - Alpha',
                   'Environment :: Web Environment',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: Zope Public License',
                   'Programming Language :: Python',
                   'Framework :: Zope3',
    ], 
      keywords="",
      author="Uli Fouquet and Jan-Ulrich Hasecke",
      author_email="uli@gnufix.de",
      url="http://cheeseshop.python.org/GrokIMDB",
      license="ZPL",
      package_dir={'': 'src'},
      packages=find_packages('src'),
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'grok',
                        # Add extra requirements here
                        'IMDbPY',
                        ],
      entry_points="""
      # Add entry points here
      """,
      )
