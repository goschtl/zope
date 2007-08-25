from setuptools import setup, find_packages

setup(name='TodoList',
      version='0.1',
      description="A todo list application",
      long_description="", # TODO
      # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[], 
      keywords="",
      author="Philipp von Weitershausen",
      author_email="philipp@weitershausen.de",
      url="",
      license="ZPL",
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'grok',
                        'hurry.query',
                        'megrok.kiss',
                        ],
      entry_points="""
      [paste.app_factory]
      main = todolist.application:application_factory
      """,
      )
