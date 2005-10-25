from setuptools import find_packages
from setuptools import setup

setup(
    name='rotten',
    version='0.1',
    packages=find_packages(),
    namespace_packages=['Products'],
    package_data={'': ['*.txt'],
                  'Products.Rotten': ['skins/rotten/*',
                                      'profiles/rotten/*',
                                     ],
                 },
)
