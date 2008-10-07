from setuptools import setup, find_packages

version = '0.0'

setup(name='SmallELearningDemo',
      version=version,
      description="",
      long_description="""\
""",
      # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[], 
      keywords="",
      author="Yusei Tahara",
      author_email="yusei@domen.cx",
      url="http://qwik.jp/zope3study/",
      license="ZPL2.1",
      package_dir={'': 'src'},
      packages=find_packages('src'),
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'grok',
                        'grokui.admin',
                        'z3c.testsetup',
                        'zope.app.file',
                        'zope.file',
                        'zope.mimetype',
                        # Add extra requirements here
                        ],
      entry_points="""
      # Add entry points here
      """,
      )
