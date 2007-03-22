#!python
from setuptools import setup, find_packages

setup(name='lovely.viewcache',
      version='0.1',
      author="Stephan Richter, Jodok Batlogg",
      author_email="srichter@cosmos.phy.tufts.edu, jodok.batlogg@lovelysystems.com",
      description="A view cache for zope 3",
      license = "ZPL 2.1",
      keywords = "zope3 web20 zope view cache",
      url='svn://svn.zope.org/repos/main/lovely.viewcache',

      packages=find_packages('src'),
      include_package_data=True,
      package_dir = {'':'src'},
      namespace_packages=['lovely'],
      install_requires=['setuptools',
                        'zope.interface',
                        'zope.component',
                        'lovely.mount',
                        ],
      extras_require={"test": ["zope.app.testing", "z3c.configurator"]},
      dependency_links=['http://download.zope.org/distribution'],
      )
