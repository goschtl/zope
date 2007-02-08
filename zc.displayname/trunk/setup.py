from setuptools import setup, find_packages

setup(
    name = "zc.displayname",
    version = "1.1dev",

    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['zc'],
    install_requires = [
    'setuptools',
    # XXX leaving out most of the zope 3 dependencies for now,
    # since Zope 3 hasn't been packaged yet.
    ],
    zip_safe=False,
    author='Zope Project',
    author_email='zope3-dev@zope.org',
    description=open("README.txt").read(),
    long_description=open("src/zc/displayname/adapters.txt").read(),
    license='ZPL 2.1',
    keywords="zope zope3",
    dependency_links = ['http://download.zope.org/distribution/'],
    )
