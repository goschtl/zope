#!python
from setuptools import setup, find_packages

setup(name='z3c.configurator',
      version='0.1',
      author = "Zope Community",
      author_email = "zope3-dev@zope.org",
      description = "Dynamic configuration",
      license = "ZPL 2.1",
      keywords = "zope zope3",
      url='http://svn.zope.org/z3c.configurator',

      zip_safe=False,
      packages=find_packages('src'),
      include_package_data=True,
      package_dir = {'':'src'},
      namespace_packages=['z3c',],
      install_requires = ['setuptools', ],
     )

