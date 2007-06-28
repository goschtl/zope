import os

from setuptools import setup, find_packages

setup(
    name='zc.twist',
    version='0.1',
    packages=find_packages('src'),
    package_dir={'':'src'},
    url='http://svn.zope.org/zc.twist',
    zip_safe=False,
    author='Gary Poster',
    description='Mixing Twisted and ZODB',
    license='ZPL',
    install_requires=[
        'ZODB3',
        'zope.component',
        'setuptools',
        'twisted ==2.1dev',
        'zope.testing',
        ],
    include_package_data=True,
    )
