from setuptools import setup, find_packages

setup(
    name = 'externalmethod',
    version = '0.1',
    packages = find_packages(),
    entry_points = {'zope2.initialize':
                    ['initialize=externalmethod:initialize']},
    url = 'http://www.example.com/externalmethod',
    author = 'Joe Bloggs',
    author_email = 'bloggs@example.com',
    zip_safe = False,
    )
