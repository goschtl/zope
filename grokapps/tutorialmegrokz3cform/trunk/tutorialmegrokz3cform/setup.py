from setuptools import setup, find_packages

version = '0.0'

setup(name='tutorialmegrokz3cform',
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
      license="ZPL",
      package_dir={'': 'src'},
      packages=find_packages('src'),
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'grok',
                        'grokui.admin',
                        'z3c.testsetup',
                        'grokcore.startup',
                        # Add extra requirements here
			'megrok.layout',
                        ],
      entry_points = """
      [console_scripts]
      tutorialmegrokz3cform-debug = grokcore.startup:interactive_debug_prompt
      tutorialmegrokz3cform-ctl = grokcore.startup:zdaemon_controller
      [paste.app_factory]
      main = grokcore.startup:application_factory
      """,
      )
