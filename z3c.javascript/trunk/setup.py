#!python
from setuptools import setup, find_packages

setup(name='z3c.javascript',
      version='0.1',
      author = "Zope Community",
      author_email = "zope3-dev@zope.org",
      description = "Javascript libraries Zope 3",
      license = "see LICENSES.txt",
      keywords = "zope zope3 javascript",
      url='http://svn.zope.org/z3c.javascript',
      zip_safe=False,
      packages=find_packages('src'),
      include_package_data=True,
      package_dir = {'':'src'},
      namespace_packages=['z3c',],
      extras_require = dict(test=['zope.testing',
                                  ]),
      install_requires = ['setuptools',
                          ],
      )

