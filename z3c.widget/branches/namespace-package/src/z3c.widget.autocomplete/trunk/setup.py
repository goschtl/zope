#!python
from setuptools import setup, find_packages

setup(name='z3c.widget.autocomplete',
      version='0.1dev',
      author = "Zope Community",
      author_email = "zope3-dev@zope.org",
      description = "z3c.widget.autocomplete provides an alternative widget "
                    "to normal select widgets",
      license = "ZPL 2.1",
      keywords = "zope zope3",
      url='http://svn.zope.org/z3c.widget', # TODO! has to be changed
      zip_safe=False,
      packages=find_packages(),
      include_package_data=True,
      namespace_packages=['z3c.widget',],
      extras_require = dict(test=['zope.app.testing',
                                  'zope.testing',
                                  'zope.app.securitypolicy',
                                  'zope.app.zcmlfiles',
                                  'zope.testbrowser',
                                  ]),
      install_requires = ['setuptools',
                          'zope.traversing',
                          'zope.security',
                          'zope.publisher',
                          'zope.formlib',
                          'zope.schema',
                          'zope.interface',
                          'zope.app.form',
                          'zc.resourcelibrary',
                          ],
      dependency_links = ['http://download.zope.org/distribution']
      )

