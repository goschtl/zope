import os
from setuptools import setup, find_packages

version = '0.1'

setup(name='z3c.gibberish',
      version=version,
      description="Generate CSV files containing random words from a dictionary",
      long_description=file(os.path.join(
            os.path.dirname(__file__), 'z3c', 'gibberish',
            'README.txt')).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Ross Patterson',
      author_email='me@rpatterson.net',
      url='http://cheeseshop.python.org/pypi/z3c.gibberish',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['z3c'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      extras_require=dict(test=['zc.buildout']),
      entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      gibberish = z3c.gibberish:main
      """,
      )
