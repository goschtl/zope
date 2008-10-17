from setuptools import setup, find_packages
import sys, os

setup(
    name='z3c.relationfieldui',
    version='0.1dev',
    description="A widget for z3c.relationfield.",
    classifiers=[],
    keywords='',
    author='Martijn Faassen',
    author_email='faassen@startifact.com',
    license='',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['z3c'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'z3c.relationfield',
        ],
    entry_points={},
    )
