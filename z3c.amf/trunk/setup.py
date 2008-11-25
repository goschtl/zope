from setuptools import setup, find_packages
import os

version = '0.2'

setup(name='z3c.amf',
      version=version,
      description="Zope support for Flash messages (AMF)",
      long_description=open(os.path.join("z3c", "amf",
                                         "README.txt")).read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Environment :: Web Environment",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "License :: OSI Approved :: Zope Public License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Site Management",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='Zope2 Zope AMF Flash Flex',
      author='Jean-Francois Roche',
      author_email='jfroche@affinitic.be',
      url='http://svn.zope.org/z3c.amf',
      license='ZPL 2.1',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['z3c'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'pyamf',
          'Products.CMFCore',
          'Products.PluggableAuthService'
      ])
