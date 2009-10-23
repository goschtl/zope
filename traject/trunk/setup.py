import os
from setuptools import setup, find_packages

version = '0.1dev'

def read(*filenames):
    return open(os.path.join(os.path.dirname(__file__), *filenames)).read()

setup(name='traject',
      version=version,
      description="A URL dispatch to object system that combines aspects of routing and traversal.",
      # long_description=read('README.txt'),
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
      keywords="route routing url traverse traversing web",
      author="Martijn Faassen",
      author_email="faassen@startifact.com",
      license="ZPL",
      package_dir={'': 'src'},
      packages=find_packages('src'),
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'zope.interface',
                        ],
      entry_points="""
      # Add entry points here
      """,
      )
