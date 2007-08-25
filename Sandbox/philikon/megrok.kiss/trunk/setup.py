from setuptools import setup, find_packages

setup(name='megrok.kiss',
      version='0.1',
      description="KSS integration for grok",
      long_description="", # TODO
      # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[], 
      keywords="",
      author="Philipp von Weitershausen",
      author_email="philipp@weitershausen.de",
      url="",
      license="ZPL",
      package_dir={'': 'src'},
      packages=find_packages('src'),
      namespace_packages=['megrok',],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'zope.component',
                        'zope.traversing',
                        'zope.publisher',
                        'kss.core',
                        'martian',
                        'grok',  # only needed for ZCML
                        ],
      )
