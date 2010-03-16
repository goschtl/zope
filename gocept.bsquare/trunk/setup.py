import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name='gocept.bsquare',
    version='0.1.0-dev',
    author='Zope Foundation and Contributors',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    license="ZPL 2.1",
    install_requires=[
        'setuptools',
        'buildbot',
        ],
    include_package_data=True,
    zip_safe=False)
