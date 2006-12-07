from setuptools import setup, find_packages

setup(
    name = "zc.shortcut",
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
    zip_safe=False,
    author='Zope Project',
    author_email='zope3-dev@zope.org',
    description=open("README.txt").read(),
    long_description=
        open("src/zc/shortcut/shortcut.txt").read() +
        '\n' +
        open("src/zc/shortcut/proxy.txt").read() +
        '\n' +
        open("src/zc/shortcut/adapters.txt").read() +
        '\n' +
        open("src/zc/shortcut/adding.txt").read() +
        '\n' +
        open("src/zc/shortcut/factory.txt").read(),
    license='ZPL 2.1',
    keywords="zope zope3",
    dependency_links = ['http://download.zope.org/distribution/'],
    )
