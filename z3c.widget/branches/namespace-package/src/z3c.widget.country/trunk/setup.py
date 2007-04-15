#!python
from setuptools import setup, find_packages

setup(name='z3c.widget.country',
      version='0.1dev',
      author = "Zope Community",
      author_email = "zope3-dev@zope.org",
      description = "z3c.widget.namespace provides widgets to select a "
                    "country",
      license = "ZPL 2.1",
      keywords = "zope zope3",
      url='http://svn.zope.org/z3c.widget', # TODO! has to be changed
      zip_safe=False,
      packages=find_packages(),
      include_package_data=True,
      namespace_packages=['z3c.widget',],
      extras_require = dict(test=['zope.app.testing',
                                  'zope.testing',
                                  ]),
      install_requires = ['setuptools',
                          'zope.app.form',
                          'zope.schema',
                          'zope.interface',
                          'z3c.i18n',
                          ],
      dependency_links = ['http://download.zope.org/distribution']
      )

