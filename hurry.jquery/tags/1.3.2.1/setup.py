from setuptools import setup, find_packages

JQUERY_VERSION = '1.3.2'

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
    name='hurry.jquery',
    version=JQUERY_VERSION + '.1',
    description="hurry.resource style resources for jQuery.",
    long_description = long_description,
    classifiers=[],
    keywords='',
    author='Jan-Wijbrand Kolman',
    author_email='jw@n--tree.net',
    license='ZPL 2.1',
    packages=find_packages('src'),
    namespace_packages=['hurry'],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'hurry.resource > 0.2',
        ],
    entry_points= {
        'console_scripts': [
            'jqueryprepare = hurry.jquery.prepare:main',
            ]
    },
    extras_require={
        'zopesupport': ['hurry.zoperesource'],
        },
    )
