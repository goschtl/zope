from setuptools import setup, find_packages
import os

version = '0.2'

setup(name='z3c.recipe.egg',
      version=version,
      description="Recipies based on zc.recipe.egg for working with source distributions.",
      long_description=open(os.path.join(os.path.dirname(__file__),
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
      url='http://cheeseshop.python.org/pypi/z3c.recipe.egg',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['z3c', 'z3c.recipe'],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'zc.recipe.egg',
      ],
      extras_require=dict(test=['zc.buildout', 'zc.recipe.egg']),
      entry_points="""
      # -*- Entry points: -*-
      [zc.buildout]
      setup = z3c.recipe.egg:Setup
      editable = z3c.recipe.egg:Editable
      """,
      )
