from setuptools import setup, find_packages

version = '0.0'

setup(name='tfws.website',
      version=version,
      description="",
      long_description="""\
""",
      # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
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
                        'lxml',
                        'grok',
                        'zope.app.file',
                        'z3c.etestbrowser',
                        'z3c.breadcrumb',
                        'z3c.configurator',
                        'z3c.form',
                        'z3c.formjs',
                        'z3c.formui',
                        'z3c.layer',
                        'z3c.pagelet',
                        'z3c.schema',
                        'z3c.template',
                        'z3c.testing',
                        'z3c.viewlet',
                        'z3c.zrtresource',
                        'z3c.formdemo',
                        'zc.resourcelibrary',
                        'zc.table',
                        'jquery.javascript',
                        'jquery.layer',
                        'mars.adapter',
                        'mars.contentprovider',
                        'mars.form',
                        'mars.layer',
                        'mars.macro',
                        'mars.resource',
                        'mars.template',
                        'mars.view',
                        'mars.viewlet',
                        # Add extra requirements here
                        ],
      entry_points="""
      [paste.app_factory]
      main = tfws.website.application:application_factory
      """,
      )
