import os

from setuptools import setup, find_packages

long_description = (open("src/zc/twist/README.txt").read() +
                    '\n\n=======\nChanges\n=======' +
                    open("CHANGES.txt").read())

setup(
    name='zc.twist',
    version='1.0',
    packages=find_packages('src'),
    package_dir={'':'src'},
    zip_safe=False,
    author='Gary Poster',
    description=open('README.txt').read(),
    long_description=long_description,
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
