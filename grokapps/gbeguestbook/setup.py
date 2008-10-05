from setuptools import setup, find_packages

version = '0.1'

setup(name='gbeguestbook',
      version=version,
      description="Grok-by-Example: Guestbook",
      long_description="""\
      base app: Google Appengine demo application
      http://code.google.com/p/googleappengine/source/browse/trunk/demos/guestbook/guestbook.py
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
                        'grokui.admin',
                        'z3c.testsetup',
                        # Add extra requirements here
                        ],
      entry_points="""
      # Add entry points here
      """,
      )
