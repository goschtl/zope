import os
from setuptools import setup, find_packages

version = '1.0'

def read(*filenames):
    return open(os.path.join(os.path.dirname(__file__), *filenames)).read()

setup(name='megrok.trails',
      version=version,
      description="URL patterns for Grok applications",
      long_description=read('README.txt'),
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
      keywords="grok megrok trail trails url",
      author="Brandon Craig Rhodes",
      author_email="brandon@rhodesmill.org",
      license="ZPL",
      package_dir={'': 'src'},
      namespace_packages=['megrok'],
      packages=find_packages('src'),
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'grok',
                        # Add extra requirements here
                        ],
      entry_points="""
      # Add entry points here
      """,
      )
