from setuptools import setup, find_packages
import os

version = '0.1'

tests_require = [
    "zope.app.appsetup",
    "zope.app.publication",
    "zope.app.publisher",
    "zope.app.testing",
    "zope.app.wsgi >= 3.9.2",
    "zope.component",
    "zope.container",
    "zope.principalregistry",
    "zope.publisher",
    "zope.schema",
    "zope.security",
    "zope.securitypolicy",
    "zope.site",
    "zope.testing",
    "zope.traversing",
    ]



setup(name='megrok.attributetraverser',
      version=version,
      description="Grokker for attribute Traversal of grok.Views",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='',
      author_email='',
      url='http://svn.plone.org/svn/collective/',
      license='GPL',
      package_dir={'': 'src'},
      packages=find_packages('src'),
      namespace_packages=['megrok'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'grok',
          # -*- Extra requirements: -*-
      ],
      extras_require={'test': tests_require},
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
