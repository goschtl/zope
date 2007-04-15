#!python
from setuptools import setup, find_packages

setup(name='z3c.widget.flashupload',
      version='0.1dev',
      author = "Zope Community",
      author_email = "zope3-dev@zope.org",
      description = "z3c.widget.namespace provides an upload widget",
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
                          'zope.app.container',
                          'zope.app.pagetemplate',
                          'zope.security',
                          'zope.filerepresentation',
                          'zope.publisher',
                          'zope.interface',
                          'zope.event',
                          'zope.component',
                          'zope.i18nmessageid',
                          'zope.app.cache',
                          'zope.traversing',
                          ],
      dependency_links = ['http://download.zope.org/distribution']
      )

