from setuptools import setup, find_packages

WFORMS_VERSION = '3.0'

import sys, os

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.txt')
    + '\n' +
    read('CHANGES.txt')
    + '\n' +
    'Download\n'
    '********\n'
    )

setup(
    name='hurry.js.wforms',
    version=WFORMS_VERSION + 'dev',
    description="wforms for hurry.resource.",
    long_description=long_description,
    classifiers=[],
    keywords='',
    author='Martijn Faassen',
    author_email='faassen@startifact.com',
    license='LGPL', # ZPL 2.1 for python code, LPGL for JS bundled
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['hurry', 'hurry.js'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'hurry.resource',
        ],
    )
