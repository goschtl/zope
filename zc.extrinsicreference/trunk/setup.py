from setuptools import setup, find_packages

setup(
    name="zc.extrinsicreference",
    version="1.0dev",
    license = 'ZPL 2.1',
    description = '',
    author = 'Zope Corporation and Contributors',
    author_email = 'zope-dev@zope.org',
    packages=find_packages('src'),
    package_dir={'':'src'},
    namespace_packages=['zc'],
    include_package_data=True,
    install_requires = [
        'ZODB3',
        'setuptools',
        'zc.shortcut',
        'zope.app.keyreference',
#        'zope.app.testing',
        'zope.interface',
        'zope.location',
        'zope.testing',
        ],
    zip_safe = False
    )
