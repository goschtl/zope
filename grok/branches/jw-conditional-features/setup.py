from setuptools import setup, find_packages
import os

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.txt')
    + '\n' +
    read('CHANGES.txt')
    + '\n' +
    'Download\n'
    '********\n'
    )

classic_require = [
    'grokcore.annotation >= 1.3',
    'grokcore.catalog',
    'grokcore.formlib >= 1.4',
    'grokcore.json >= 1.2dev',
    'grokcore.message',
    'grokcore.rest >= 1.3dev',
    'grokcore.security[role] >= 1.6dev',
    'grokcore.viewlet >= 1.10dev',
    'grokcore.xmlrpc >= 1.2dev',
    'simplejson',
    'zc.catalog',
    'zope.annotation',
    'zope.catalog',
    'zope.errorview [browser]',
    'zope.i18n',
    'zope.i18nmessageid',
    'zope.login',
    'zope.securitypolicy',
    'zope.password',
    'zope.principalregistry',
    ]
tests_require = [
    'grokcore.chameleon',
    'grokcore.layout',
    'grokcore.message',
    'zope.app.wsgi',
    'zope.configuration',
    'zope.testing',
    ] + classic_require

setup(
    name='grok',
    version='1.11.dev0',
    author='Grok Team',
    author_email='grok-dev@zope.org',
    url='http://grok.zope.org',
    download_url='http://cheeseshop.python.org/pypi/grok/',
    description='Grok: Now even cavemen can use Zope 3!',
    long_description=long_description,
    license='ZPL',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Framework :: Zope3',
        ],
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data = True,
    zip_safe=False,
    install_requires=[
        'grokcore.component >= 2.5',
        'grokcore.content >= 1.1',
        'grokcore.security >= 1.6',
        'grokcore.site >= 1.6.1',
        'grokcore.traverser >= 1.1',
        'grokcore.view >= 2.7',
        'grokcore.view [security_publication]',
        'martian >= 0.14',
        'pytz',
        'setuptools',
        'z3c.autoinclude',
        'zc.catalog',
        'ZODB3',
        'zope.app.appsetup',
        'zope.app.publication',
        'zope.app.wsgi',
        'zope.browserpage',
        'zope.component',
        'zope.container',
        'zope.contentprovider',
        'zope.errorview[browser]',
        'zope.event',
        'zope.exceptions',
        'zope.interface',
        'zope.intid',
        'zope.keyreference',
        'zope.lifecycleevent',
        'zope.location',
        'zope.login',
        'zope.password',
        'zope.principalregistry',
        'zope.publisher',
        'zope.schema',
        'zope.security',
        'zope.site',
        'zope.traversing',
        ],
    tests_require=tests_require,
    extras_require={
        'classic': classic_require,
        'test': tests_require,
        },
)
