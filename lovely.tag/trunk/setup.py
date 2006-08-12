#!python
from setuptools import setup, find_packages

setup(name='lovely.tag',
      version='0.1',
      author = "Stephan Richter, Jodok Batlogg",
      author_email = "srichter@cosmos.phy.tufts.edu, jodok.batlogg@lovelysystems.com",
      description = "A tagging engine for zope 3",
      license = "ZPL 2.1",
      keywords = "zope3 web20 zope tagging",
      url='svn://svn.zope.org/repos/main/lovely.tag',

      packages=find_packages('src'),
      include_package_data=True,
      package_dir = {'':'src'},
      namespace_packages=['lovely'],
      install_requires = ['setuptools', ],
      dependency_links = ['https://backstage.lovelysystems.com/software/eggs'],
     )

