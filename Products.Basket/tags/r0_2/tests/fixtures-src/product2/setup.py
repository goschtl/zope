from setuptools import setup, find_packages

setup(
    name = 'product2',
    version = '0.1',
    packages = find_packages(),
    namespace_packages=['Products'],
    entry_points = {'zope2.initialize':
                    ['initialize=Products.product2:initialize']},
    url = 'http://www.example.com/product2',
    author = 'Joe Bloggs',
    author_email = 'bloggs@example.com',
    )
