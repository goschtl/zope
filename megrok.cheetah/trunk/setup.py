from setuptools import setup, find_packages

version = '0.1'

long_description = (open('README.txt').read() +
                    '\n\n' +
                    open('CHANGES.txt').read())

setup(name='megrok.cheetah',
      version=version,
      description="Integrate Cheetah Templates into Grok",
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
      keywords="grok cheetah",
      author="Paul A. Wilson",
      author_email="paulalexwilson@gmail.com",
      license="ZPL",
      package_dir={'': 'src'},
      packages=find_packages('src'),
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'grok',
                        'Cheetah',
                        ],
      entry_points="""
      # Add entry points here
      """,
      )
