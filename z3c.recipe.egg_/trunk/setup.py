from setuptools import setup, find_packages
import os.path

def read(path):
    return open(os.path.join(path), 'r').read() + '\n\n'

version = '0.3dev'

setup(name='z3c.recipe.egg',
      version=version,
      description="Recipies based on zc.recipe.egg for working with source distributions.",
      long_description=(
          '.. contents:: \n\n' +
          read('README.txt') +
          read('CHANGES.txt')),
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
      url='http://pypi.python.org/pypi/z3c.recipe.egg',
      license='ZPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['z3c', 'z3c.recipe'],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          'setuptools',
          'zc.recipe.egg >= 1.3.0',
      ],
      extras_require=dict(
          test=[
              'zc.buildout >= 1.5.0',
              'zc.recipe.egg',
              'zope.testing',
              'z3c.recipe.scripts',
              ]),
      entry_points="""
      # -*- Entry points: -*-
      [zc.buildout]
      setup = z3c.recipe.egg:Setup
      editable = z3c.recipe.egg:Editable
      """,
      )
