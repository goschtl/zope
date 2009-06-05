from setuptools import setup, find_packages
import os

version = '1.0dev'

install_requires = [
    'setuptools',
    'grokcore.view',
    'z3c.pt >= 1.0b4',
    ]

# The grok dependency is not added explicitly, so we can factor out a
# version of this package for Zope 2 which is not going to install
# grok. But we want the dependency to run tests.
test_requires = install_requires + ['grok >= 0.14',]

setup(name='megrok.z3cpt',
      version=version,
      description="z3c.pt support for Grok",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          "Environment :: Web Environment",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: Zope Public License",
          "Programming Language :: Python",
          "Topic :: Software Development :: Libraries :: Python Modules",
          "Framework :: Zope3",
          ],
      keywords='pagetemplate grok',
      author='Sylvain Viollon',
      author_email='grok-dev@zope.org',
      url='http://svn.zope.org/megrok.z3cpt',
      license='ZPL',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['megrok'],
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      extras_require={'test': test_requires,},
      )
