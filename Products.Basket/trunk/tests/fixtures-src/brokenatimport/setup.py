from setuptools import setup, find_packages

setup(
    name = 'brokenatimport',
    version = '0.1',
    packages = find_packages(),
    entry_points = {'zope2.initialize':
                    ['initialize=brokenatimport:initialize']},
    url = 'http://www.example.com/brokenatimport',
    author = 'Joe Bloggs',
    author_email = 'bloggs@example.com',
    )
