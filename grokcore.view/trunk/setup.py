from setuptools import setup, find_packages
import os

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.txt')
    + '\n' +
    read('CHANGES.txt')
    )

tests_require = [
    'zope.app.authentication',
    'zope.app.basicskin',
    'zope.app.container',
    'zope.app.rotterdam',
    'zope.app.testing',
    'zope.app.zcmlfiles',
    'zope.configuration',
    'zope.securitypolicy',
    'zope.testbrowser',
    'zope.testing',
    ]

setup(
    name='grokcore.view',
    version = '2.0dev',
    author='Grok Team',
    author_email='grok-dev@zope.org',
    url='http://grok.zope.org',
    download_url='http://pypi.python.org/pypi/grok/',
    description='Grok-like configuration for Zope browser pages',
    long_description=long_description,
    license='ZPL',
    classifiers=['Environment :: Web Environment',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: Zope Public License',
                 'Programming Language :: Python',
                 'Framework :: Zope3',
                 ],

    packages=find_packages('src'),
    package_dir = {'': 'src'},
    namespace_packages=['grokcore'],
    include_package_data = True,
    zip_safe=False,
    install_requires=['setuptools',
                      'grokcore.component >= 2.0',
                      'grokcore.security >= 1.3',
                      'martian >= 0.12',
                      'zope.app.pagetemplate',
                      'zope.app.publisher >= 3.5',
                      'zope.component',
                      'zope.interface',
                      'zope.pagetemplate',
                      'zope.publisher',
                      'zope.security',
                      'zope.traversing',
                      ],
    tests_require=tests_require,
    extras_require={'test': tests_require},
)
