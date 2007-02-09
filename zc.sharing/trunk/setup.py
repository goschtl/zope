from setuptools import setup, find_packages

setup(
    name = "zc.sharing",
    version = "1.1dev",
    author = "Zope Corporation",
    author_email = "zope3-dev#zope.org",
    description = "Zope 3 security policy",
    license = "ZPL 2.1",
    keywords = "zope3 security",
    url='http://svn.zope.org/zc.sharing',

    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['zc'],
    install_requires = [
       'zc.table',
       'zc.security',
       'zope.testing',
       'setuptools',
       # XXX leaving out most of the zope 3 dependencies for now,
       # since Zope 3 hasn't been packages yet.
       ],
    dependency_links = ['http://download.zope.org/distribution/'],
    )
