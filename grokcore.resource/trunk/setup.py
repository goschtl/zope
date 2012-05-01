from setuptools import setup, find_packages
import os.path

version = '1.0dev'

README = open(os.path.join('src', 'grokcore', 'resource', 'README.txt')).read()
CHANGES = open('CHANGES.txt').read()

long_description = '%s\n%s' % (README, CHANGES)

setup(name='grokcore.resource',
    version=version,
    author='Grok Team',
    author_email='grok-dev@zope.org',
    url='http://pypi.python.org/pypi/grokcore.resource',
    download_url='http://pypi.python.org/pypi/grokcore.resource',
    description='Grok Resources based on fanstatic',
    long_description=long_description,
    keywords='Grok Resources fanstatic',
    license='ZPL',
    classifiers=['Intended Audience :: Developers',
                 'License :: OSI Approved :: Zope Public License',
                 'Programming Language :: Python',
                 ],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['grokcore'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'fanstatic >= 0.11',
        'grokcore.component',
        'martian',
        'setuptools',
        'zope.app.publication',
        'zope.interface',
        'zope.security',
        ],
    extras_require={'test': [
        'grokcore.view',
        'zope.app.wsgi',
        'zope.browserpage',
        'zope.fanstatic',
        'zope.principalregistry',
        'zope.securitypolicy',
        ]
    },
)
