from setuptools import setup, find_packages

setup(
    name = 'fiveproduct',
    version = '0.1',
    packages = find_packages(),
    package_data = {'':['*.zcml', '*.pt']},
    namespace_packages=['Products'],
    entry_points = {'zope2.initialize':
                    ['initialize=Products.fiveproduct:initialize']},
    url = 'http://www.example.com/fiveproduct',
    author = 'Joe Bloggs',
    author_email = 'bloggs@example.com',
    zip_safe = False,
    )
