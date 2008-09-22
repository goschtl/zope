from setuptools import setup, find_packages
import sys, os

setup(
    name='hurry.resource',
    version='0.1dev',
    description="Flexible resources.",
    classifiers=[],
    keywords='',
    author='Martijn Faassen',
    author_email='faassen@startifact.com',
    license='',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'zope.interface',
        'zope.component',
        ],
    entry_points={},
    )
