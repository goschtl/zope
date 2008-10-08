from setuptools import setup, find_packages

version = '0.1'

setup(name='gbedemosite',
      version=version,
      description="Grok-by-Example",
      long_description="""\
      create a multi-application demosite
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
                        'gbewiki',
                        'gbeguestbook',
                        'gbe99bottles',
                        'gbepastebin',
                        ],
      entry_points="""
      # Add entry points here
      """,
      )
