import sys
from setuptools import setup, find_packages

install_requires = [
    'setuptools',
    'zope.testing',
    ]

if sys.version_info < (2, 6, 0):
    install_requires.append('ssl-for-setuptools')

setup(
    name = "zc.ssl",
    version = "1.2",
    author = "Zope Corporation",
    author_email = "zope-dev@zope.org",
    description = "An HTTPSConnection implementation with the new ssl module",
    keywords = "ssl https",
    packages = find_packages('src'),
    include_package_data = True,
    zip_safe = False,
    package_dir = {'':'src'},
    namespace_packages = ['zc'],
    install_requires = install_requires,
    dependency_links = ['http://download.zope.org/distribution/'],
    license = "ZPL 2.1",
    )
