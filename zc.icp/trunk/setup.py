import os

from setuptools import setup, find_packages

setup(
    name='zc.icp',
    version='1.0dev',
    packages=find_packages('src', exclude=['*.tests', '*.ftests']),
    package_dir={'':'src'},

    url='svn+ssh://svn.zope.com/repos/main/zc.icp',
    zip_safe=False,
    author='Zope Corporation',
    author_email='benji@zope.com',
    description='Pluggable ICP server',
    license='ZPL',
    install_requires=[
        'setuptools',
        'zope.component',
        'zope.interface',
        'zope.testing',
        ],
    include_package_data=True,
    )
