from setuptools import setup, find_packages

import sys, os

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = ''
#(
#    read('README.txt')
#    + '\n' +
#    read('CHANGES.txt')
#    + '\n' +
#    'Download\n'
#    '********\n'
#    )


setup(
    name='hurry.explorer',
    version='0.1dev',
    description="An explorer UI built with YUI.",
    long_description = long_description,
    classifiers=[],
    keywords='',
    author='Martijn Faassen',
    author_email='faassen@startifact.com',
    license='ZPL 2.1',
    packages=find_packages('src'),
    namespace_packages=['hurry'],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'hurry.resource > 0.2',
        'hurry.yui',
        ],
    )
