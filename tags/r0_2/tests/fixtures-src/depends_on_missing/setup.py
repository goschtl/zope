from setuptools import setup, find_packages

setup(
    name = 'depends_on_missing',
    version = '0.1',
    packages = find_packages(),
    entry_points = {'zope2.initialize':
                    ['initialize=Products.depends_on_missing:initialize']},
    url = 'http://www.example.com/depends_on_missing',
    author = 'Joe Bloggs',
    author_email = 'bloggs@example.com',
    install_requires=['missingpackage'],
    )
