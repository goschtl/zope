from setuptools import setup, find_packages

setup(
    name = 'externaleditor',
    version = '0.9.2',
    packages = find_packages(),
    namespace_packages = ['Products'],
    entry_points = {
      'zope2.initialize':
      ['initialize=Products.ExternalEditor:__name__']
      },
    package_data = {
        'Products.ExternalEditor': ['*.gif','*.txt','*.dtml', 'man/zopeedit*',
                                    'win32/*.iss', 'win32/*.txt', 'win32/*.ocx',
                                    'win32/*.ini', 'win32/*.bat']
        },
    url = 'http://www.plope.com/software/ExternalEditor',
    author = 'Casey Duncan',
    maintainer = 'Chris McDonough',
    maintainer_email = 'chrism@plope.com',
    zip_safe = True,
    )
