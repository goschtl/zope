from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='z3c.recipe.template',
      version=version,
      description="Buildout recipe to generate a text file from a template",
      long_description=open("README.txt").read() + "\n\n" +
                       open(os.path.join("z3c", "recipe", "template",
                                         "README.txt")).read() + "\n\n" +
                       open("CHANGES.txt").read(),
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: Buildout",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: Zope Public License",
        ],
      keywords='template buildout zope',
      author='Uli Fouquet based on work of Wichert Akkerman',
      author_email='grok-dev@zope.org',
      url='http://pypi.python.org/pypi/z3c.recipe.template',
      license='ZPL 2.1',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['z3c', 'z3c.recipe' ],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'zc.buildout',
      ],
      extras_require=dict(
        test = [
            'zope.testing',
            ]
        ),
      entry_points="""
      [zc.buildout]
      default = z3c.recipe.template:Recipe
      """,
      )
