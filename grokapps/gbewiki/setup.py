from setuptools import setup, find_packages

version = '0.1'

setup(name='gbewiki',
      version=version,
      description="Grok-by-Example: Wiki",
      long_description="""\
      ported from 
http://code.google.com/p/google-app-engine-samples/source/browse/trunk/cccwiki/
""",
      # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[], 
      keywords="grok example",
      author="d2m",
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
                        'megrok.tinymce',
                        ],
      entry_points="""
      # Add entry points here
      """,
      )
