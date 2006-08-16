#!python
from setuptools import setup, find_packages

setup(name='z3c.configurator',
      version='0.1',
      author = "??",
      author_email = "office@lovelysystems.com",
      description = "Dynamic configuration",
      license = "ZPL 2.1",
      keywords = "zope zope3",
      url='http://svn.zope.org/z3c.configurator',
      packages=find_packages('src'),
      include_package_data=True,
      package_dir = {'':'src'},
      namespace_packages=['refline',],
      install_requires = ['setuptools', ],
     )

