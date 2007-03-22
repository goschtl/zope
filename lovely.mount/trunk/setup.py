#!python
from setuptools import setup, find_packages

setup(name='lovely.mount',
      version='0.1',
      author="Stephan Richter, Jodok Batlogg",
      author_email="srichter@cosmos.phy.tufts.edu, jodok.batlogg@lovelysystems.com",
      description="Database mounts for zope 3",
      license = "ZPL 2.1",
      keywords = "zope3 web20 zope database mount",
      url='svn://svn.zope.org/repos/main/lovely.mount',

      packages=find_packages('src'),
      include_package_data=True,
      package_dir = {'':'src'},
      namespace_packages=['lovely'],
      install_requires=['setuptools',
                        'zope.interface',
                        'zope.component',
                        ],
      extras_require={"test": ["zope.app.testing"]},
      dependency_links=['http://download.zope.org/distribution'],
      )
