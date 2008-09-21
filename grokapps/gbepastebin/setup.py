from setuptools import setup, find_packages

version = '0.1'

setup(name='gbepastebin',
      version=version,
      description="Grok-by-Example: PasteBin",
      long_description="""\
      Simple PasteBin implementation
      porting both ClueBin and ClueGun
""",
      # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=['Development Status :: 4 - Beta',
                   'Framework :: Zope3',
                   'License :: OSI Approved :: Zope Public License',
                   'Programming Language :: Python',
                   'Programming Language :: Zope',
                   ], 
      keywords="Grok Example",
      author="Michael Haubenwallner",
      author_email="michael@d2m.at",
      url="http://blog.d2m.at",
      license="ZPL2",
      package_dir={'': 'src'},
      packages=find_packages('src'),
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'grok',
                        'z3c.testsetup',
                        # Add extra requirements here
                        'Pygments',
                        ],
      entry_points="""
      # Add entry points here
      """,
      )
