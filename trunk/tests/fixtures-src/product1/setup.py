from setuptools import setup, find_packages

setup(
    name = 'product1',
    version = '0.1',
    packages = find_packages(),
    namespace_packages=['Products'],
    entry_points = {'zope2.initialize':
                    ['initialize=Products.product1:initialize']},
    url = 'http://www.example.com/product1',
    author = 'Joe Bloggs',
    author_email = 'bloggs@example.com',
    )
