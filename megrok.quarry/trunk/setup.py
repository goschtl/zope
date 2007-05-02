from setuptools import setup, find_packages

version = '0.1'

setup(name='megrok.quarry',
      version=version,
      description="Skins and layers for Grok.",
      long_description="""\
""",
      # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[], 
      keywords="",
      author="Kevin Smith",
      author_email="kevin@mcweekly.com",
      url="",
      license="ZPL",
      package_dir={'': 'src'},
      packages=find_packages('src'),
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'grok',
                        # -*- Extra requirements: -*-
                        ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
