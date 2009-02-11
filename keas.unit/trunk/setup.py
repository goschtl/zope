import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name='keas.unit',
    version = '0.1.0-dev',
    author='Keas Inc.',
    description="A simple wrapper around the 'units' shell command",
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    extras_require=dict(
        test=['zope.testing'],
        ),
    install_requires=[
        'setuptools',
        'zope.interface',
        'zope.schema'
        ],
    include_package_data = True,
    zip_safe = False,
    )
