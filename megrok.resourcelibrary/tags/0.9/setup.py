from setuptools import setup, find_packages
import os

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('src/megrok/resourcelibrary/README.txt')
    + '\n' +
    read('CHANGES.txt')
    )

setup(name='megrok.resourcelibrary',
      version='0.9',
      description="Static resource library support for Grok.",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Grok Team',
      author_email='grok-dev@zope.org',
      url='',
      license='ZPL',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['megrok'],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          'setuptools',
          'grok >= 0.13',
          'zc.resourcelibrary',
         ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
