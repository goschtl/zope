#!python
from setuptools import setup, find_packages

setup(name='lovely.rating',
      version='0.1',
      author = "Stephan Richter",
      author_email = "srichter@cosmos.phy.tufts.edu",
      description = "A rating engine for zope 3",
      license = "ZPL 2.1",
      keywords = "zope3 web20 rating",
      url='svn://svn.zope.org/repos/main/lovely.rating',

      packages=find_packages('src'),
      include_package_data=True,
      package_dir = {'':'src'},
      namespace_packages=['lovely'],
      install_requires = ['setuptools', ],
      dependency_links = ['http://download.zope.org/distribution',
                          'http://download.lovelysystems.com/distribution'],
     )
