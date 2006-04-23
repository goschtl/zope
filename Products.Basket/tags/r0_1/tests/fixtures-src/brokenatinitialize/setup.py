from setuptools import setup, find_packages

setup(
    name = 'brokenatinitialize',
    version = '0.1',
    packages = find_packages(),
    entry_points = {'zope2.initialize':
                    ['initialize=brokenatinitialize:initialize']},
    url = 'http://www.example.com/brokenatinitialize',
    author = 'Joe Bloggs',
    author_email = 'bloggs@example.com',
    )
