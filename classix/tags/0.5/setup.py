import os

from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('src', 'classix', 'README.txt')
    + '\n' +
    read('CHANGES.txt')
    + '\n' +
    'Download\n'
    '********\n'
    )

setup(
    name='classix',
    version='0.5',
    author='Martijn Faassen',
    author_email='faassen@startifact.com',
    description="""\
Declarative way to associate classes with lxml XML elements.
""",
    long_description=long_description,
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    license='ZPL 2.1',
    include_package_data = True,
    zip_safe=False,
    install_requires=[
    'setuptools',
    'lxml == 2.0.6',
    'martian >= 0.10',
    ],
)
