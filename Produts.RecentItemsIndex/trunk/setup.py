import os
from setuptools import setup
from setuptools import find_packages

NAME = 'RecentItemsIndex'

here = os.path.abspath(os.path.dirname(__file__))
package = os.path.join(here, 'Products', NAME)
docs = os.path.join(here, 'docs')

def _package_doc(name):
    f = open(os.path.join(package, name))
    return f.read()

def _docs_doc(name):
    f = open(os.path.join(docs, name))
    return f.read()

_boundary = '\n' + ('-' * 60) + '\n\n'
README = ( open('README.txt').read()
         + _boundary
         + _docs_doc('CHANGES.rst')
         )

setup(name='Products.%s' % NAME,
      version=_package_doc('version.txt').strip(),
      description='Read Zope configuration state from profile dirs / tarballs',
      long_description=README,
      classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Plone",
        "Framework :: Zope2",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Zope Public License",
        "Programming Language :: Python",
        ],
      keywords='web application server zope zope2 cmf',
      author="Zope Corporation and contributors",
      author_email="zope-cmf@zope.org",
      url="http://pypi.python.org/pypi/Products.%s" % NAME,
      license="ZPL 2.1 (http://www.zope.org/Resources/License/ZPL-2.1)",
      packages=find_packages(),
      include_package_data=True,
      namespace_packages=['Products'],
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Zope2 >= 2.12.3',
          ],
      test_suite="Products.%s.tests" % NAME,
      entry_points="""
      [zope2.initialize]
      Products.%s = Products.%s:initialize
      """ % (NAME, NAME),
)
