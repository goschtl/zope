from setuptools import setup, find_packages

setup(
    name = "zc.ssl",
    version = "1.1",
    author = "Zope Corporation",
    author_email = "zope-dev@zope.org",
    description = "An HTTPSConnection implementation with the new ssl module",
    keywords = "ssl https",
    packages = find_packages('src'),
    include_package_data = True,
    zip_safe = False,
    package_dir = {'':'src'},
    namespace_packages = ['zc'],
    install_requires = [
       'setuptools',
       'ssl-for-setuptools',
       'zope.testing',
       ],
    dependency_links = ['http://download.zope.org/distribution/'],
    license = "ZPL 2.1",
    )
