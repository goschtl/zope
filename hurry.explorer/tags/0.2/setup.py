from setuptools import setup, find_packages

import sys, os

setup(
    name='hurry.explorer',
    version='0.2',
    description="A (object) filesystem explorer UI built with YUI.",
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
