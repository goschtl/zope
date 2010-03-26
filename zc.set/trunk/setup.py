from setuptools import setup, find_packages

setup(
    name="zc.set",
    version="0.1dev",
    license='ZPL 2.1',
    packages=find_packages('src'),
    package_dir={'':'src'},
    namespace_packages=['zc'],
    include_package_data=True,
    install_requires=[
        'setuptools',
        'ZODB3',
        'zope.app.folder',
    ],
    zip_safe=False
    )
