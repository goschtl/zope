#!python
from setuptools import setup, find_packages

setup(name='z3c.schema',
      version='0.2',
      author = "Zope Community",
      author_email = "zope3-dev@zope.org",
      description = "Additional schema fields for Zope 3",
      license = "ZPL 2.1",
      keywords = "zope zope3 schema fields",
      url='http://svn.zope.org/z3c.schema',
      zip_safe=False,
      packages=find_packages('src'),
      include_package_data=True,
      package_dir = {'':'src'},
      namespace_packages=['z3c',],
      extras_require = dict(test=['zope.testing',
                                  ]),
      install_requires = ['setuptools',
                          'zope.i18nmessageid',
                          'zope.interface',
                          'zope.schema',
                          ],
      )

