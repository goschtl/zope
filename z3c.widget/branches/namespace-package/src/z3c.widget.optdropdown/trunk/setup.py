#!python
from setuptools import setup, find_packages

setup(name='z3c.widget.optdropdown',
      version='0.1dev',
      author = "Zope Community",
      author_email = "zope3-dev@zope.org",
      description="The Optional Dropdown Widget simulates the common "
                  "desktop widget of a combo box, which can also receive "
                  "a custom entry.",
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
                          'z3c.schema',
                          'zope.app.form',
                          'zope.schema',
                          'zope.interface',
                          'zope.component',
                          ],
      dependency_links = ['http://download.zope.org/distribution']
      )

