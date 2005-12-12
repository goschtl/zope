from setuptools import setup, find_packages

setup(
    name = 'directoryview',
    version = '0.1',
    packages = find_packages(),
    package_data = {'directoryview':['skins/directoryview/*.pt']},
    entry_points = {'zope2.initialize':
                    ['initialize=directoryview:initialize']},
    url = 'http://www.example.com/directoryview',
    author = 'Joe Bloggs',
    author_email = 'bloggs@example.com',
    zip_safe = False,
    )
