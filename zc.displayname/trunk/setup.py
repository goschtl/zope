from setuptools import setup, find_packages

setup(
    name = "zc.displayname",
    description = "A Zope 3 extension for pluggable display names.",
    version = "1.0",

    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['zc'],
    install_requires = [
    'setuptools',
    # XXX leaving out most of the zope 3 dependencies for now,
    # since Zope 3 hasn't been packaged yet.
    ],
    dependency_links = ['http://download.zope.org/distribution/'],
    )
