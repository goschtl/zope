from setuptools import setup, find_packages

setup(
    name = 'fiveproduct2',
    version = '0.1',
    packages = find_packages(),
    package_data = {'':['*.zcml', '*.pt']},
    entry_points = {'zope2.initialize':
                    ['initialize=fiveproduct2:initialize']},
    url = 'http://www.example.com/fiveproduct2',
    author = 'Joe Bloggs',
    author_email = 'bloggs@example.com',
    zip_safe = False,
    )
