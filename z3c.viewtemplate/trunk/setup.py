#!python
from setuptools import setup, find_packages

setup(name='z3c.viewtemplate',
      version='0.1.1',
      author = "Zope Community",
      author_email = "zope3-dev@zope.org",
      description = open("README.txt").read(),
      license = "ZPL 2.1",
      keywords = "view template zope zope3",
      url='http://svn.zope.org/z3c.viewtemplate',

      zip_safe=False,
      packages=find_packages('src'),
      include_package_data=True,
      package_dir = {'':'src'},
      namespace_packages=['z3c',],
      extras_require = dict(test=['zope.app.testing',
                                  'zope.testing',
                                  ]),
      install_requires=[
          'setuptools',
          'zope.app.pagetemplate',
          'zope.component',
          'zope.configuration',
          'zope.contentprovider',
          'zope.i18nmessageid',
          'zope.pagetemplate',
          'zope.publisher',
          'zope.tal',
          ],
      )

