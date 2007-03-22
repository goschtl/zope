#!python
from setuptools import setup, find_packages

setup(name='z3c.configurator',
      version='1.1',
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
      extras_require = dict(test=['zope.app.testing']),
      install_requires = ['setuptools',
                          'zope.component',
                          'zope.schema',
                          ],
      dependency_links=['http://download.zope.org/distribution']
      )

