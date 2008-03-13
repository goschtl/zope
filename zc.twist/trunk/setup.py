import os

from setuptools import setup, find_packages

setup(
    name='zc.twist',
    version='1.0',
    packages=find_packages('src'),
    package_dir={'':'src'},
    zip_safe=False,
    author='Gary Poster',
    description='Mixing Twisted and ZODB',
    license='ZPL',
    install_requires=[
        'ZODB3',
        'zc.twisted', # setup-friendly Twisted distro.  Someday soon we can
        # discard zc.twisted, hopefully.  See
        # http://twistedmatrix.com/trac/ticket/1286
        'zope.component',
        'setuptools',
        'zope.testing',
        ],
    include_package_data=True,
    )
