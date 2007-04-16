#!python
from setuptools import setup, find_packages

setup(name='z3c.widget.tiny',
      version='0.1dev',
      author = "Zope Community",
      author_email = "zope3-dev@zope.org",
      description = "z3c.widget.namespace provides a WYSIWYG-Editor-Widget "
                    "for HTML-Content",
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
                          'zope.app.file',
                          'zope.schema',
                          'zope.interface',
                          ],
      dependency_links = ['http://download.zope.org/distribution']
      )

