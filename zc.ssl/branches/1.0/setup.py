from setuptools import setup, find_packages

setup(
    name = "zc.ssl",
    version = "1.0",
    author = "Zope Corporation",
    author_email = "zope3-dev#zope.org",
    description = "An HTTPSConnection implementation with the new ssl module",
    keywords = "ssl https",

    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['zc'],
    install_requires = [
       'zope.testing',
       'setuptools',
       'ssl-for-setuptools',
       ],
    dependency_links = ['http://download.zope.org/distribution/'],
    license = "ZPL 2.1",
    )
