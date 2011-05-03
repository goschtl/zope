from setuptools import setup, find_packages

setup(
    name = "zc.shortcut",
    version = "1.1",
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['zc'],
    install_requires = [
        'setuptools',
        'zc.displayname',
        'zope.decorator',
        'zope.deprecation',
        'zope.app.component',
    ],
    extras_require=dict(
        test=[
            'zope.app.testing',
            ]),
    zip_safe=False,
    author='Zope Project',
    author_email='zope-dev@zope.org',
    description=open("README.txt").read(),
    long_description=
        open("CHANGES.txt").read() +
        '\n' +
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
    )
