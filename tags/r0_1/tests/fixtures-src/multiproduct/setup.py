from setuptools import setup, find_packages

setup(
    name = 'multiproduct',
    version = '0.1',
    packages = find_packages(),
    entry_points = {'zope2.initialize':
                    ['initialize1=multiproduct1:initialize',
                     'initialize2=multiproduct2:initialize']},
    url = 'http://www.example.com/multiproduct',
    author = 'Joe Bloggs',
    author_email = 'bloggs@example.com',
    )
