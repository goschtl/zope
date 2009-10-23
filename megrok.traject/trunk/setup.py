import os
from setuptools import setup, find_packages

version = '0.1dev'

def read(*filenames):
    return open(os.path.join(os.path.dirname(__file__), *filenames)).read()

setup(name='megrok.traject',
      version=version,
      description="Traject integration for Grok applications",
      
      # Use classifiers that are already listed at:
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=['Development Status :: 5 - Production/Stable',
                   'Environment :: Web Environment',
                   'Framework :: Zope3',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: Zope Public License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Internet :: WWW/HTTP',
                   'Topic :: Software Development :: Libraries',
                   ],
      keywords="grok megrok url traject traversal routing route",
      author="Martijn Faassen",
      author_email="faassen@startifact.com",
      license="ZPL",
      package_dir={'': 'src'},
      namespace_packages=['megrok'],
      packages=find_packages('src'),
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'grok', # for grok.Traverser, ideally get rid of that
                        'traject',
                        'martian',
                        'grokcore.component',
                        'zope.publisher',
                        'zope.component',
                        ],
      entry_points="""
      # Add entry points here
      """,
      )
