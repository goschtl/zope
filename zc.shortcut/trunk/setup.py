from setuptools import setup, find_packages

setup(
    name = "zc.shortcut",
    description = "Symlinks for Zope 3",
    version = "1.0",

    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['zc'],
    install_requires = [
    'setuptools',
    'zc.displayname',
    # XXX leaving out most of the zope 3 dependencies for now,
    # since Zope 3 hasn't been packages yet.
    ],
    dependency_links = ['http://download.zope.org/distribution/'],
    )
