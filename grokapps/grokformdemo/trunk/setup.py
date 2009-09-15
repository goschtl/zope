from setuptools import setup, find_packages

version = '0.0'

setup(name='grokformdemo',
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
                        'grok',
                        'grokui.admin',
                        'z3c.testsetup',
                        'grokcore.startup',
                        'megrok.layout',
                        'megrok.z3cform.base',
                        'megrok.z3cform.layout',
                        'megrok.z3cform.wizard',
                        'z3c.csvvocabulary',
                        'hurry.jquery',
                        'hurry.zoperesource',
                        # Add extra requirements here
                        ],
      entry_points = """
      [console_scripts]
      grokformdemo-debug = grokcore.startup:interactive_debug_prompt
      grokformdemo-ctl = grokcore.startup:zdaemon_controller
      [paste.app_factory]
      main = grokcore.startup:application_factory
      """,
      )
