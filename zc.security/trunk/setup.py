from setuptools import setup, find_packages

setup(
    name = "zc.security",
    version = "4.1dev",
    author = "Zope Corporation",
    author_email = "zope3-dev@zope.org",
    description = "Principal-searching UI for Zope 3 Pluggable Authentication",
    license = "ZPL 2.1",
    keywords = "zope3 security",
    url='http://svn.zope.org/zc.sharing',
    classifiers = [
        'Development Status :: 3 - Alpha',
        "License :: OSI Approved :: Zope Public License",
        "Framework :: Zope :: UI",
        ],
    
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['zc'],
    install_requires = [
       'zope.testing',
       'setuptools',
       # XXX leaving out most of the zope 3 dependencies for now,
       # since Zope 3 hasn't been packages yet.
       ],
    dependency_links = ['http://download.zope.org/distribution/'],
    )


