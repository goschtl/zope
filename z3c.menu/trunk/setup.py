#!python
from setuptools import setup, find_packages

setup(name='z3c.menu',
      version='0.1.0',
      author = "Zope Community",
      author_email = "zope3-dev@zope.org",
      description = open("README.txt").read(),
      license = "ZPL 2.1",
      keywords = "menu zope zope3",
      url='http://svn.zope.org/z3c.menu',

      zip_safe=False,
      packages=find_packages('src'),
      include_package_data=True,
      package_dir = {'':'src'},
      namespace_packages=['z3c',],
      install_requires = [
          'setuptools',
          'zope.app',  # for zope.app.pagetemplate
          'zope.component',
          'zope.contentprovider',
          'zope.interface',
          'zope.schema',
          'zope.viewlet',
          'z3c.i18n',
          'z3c.viewlet',
          ],
      extras_require = {
          "test": [
              "zope.security",
              "zope.testing",
              "zope.traversing",
              "zope.app.testing",
              ],
          },
      dependency_links = ['http://download.zope.org/distribution/',],
     )

