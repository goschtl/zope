from setuptools import setup, find_packages

version = '1.0dev'

setup(name='megrok.feeds',
      version=version,
      description="",
      long_description="""\
""",
      # Use classifiers that are already listed at:
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[], 
      keywords="",
      author="",
      author_email="",
      url="",
      license="",
      package_dir={'': 'src'},
      packages=find_packages('src'),
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'grok',
                        # Add extra requirements here
                        'vice.outbound.core',
                        ],
      entry_points="""
      # Add entry points here
      """,
      )
