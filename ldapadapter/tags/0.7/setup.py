from setuptools import setup, find_packages

setup(
    name='ldapadapter',
    version='0.7',
    author='Zope 3 developers',
    author_email='zope3-dev@zope.org',
    url='http://svn.zope.org/ldapadapter',
    description="""\
LDAP connection for Zope 3. Connects Zope 3 to an LDAP server.
""",
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data = True,
    zip_safe=False,
    license='ZPL 2.1',
    keywords='Zope3 authentication ldap',
    classifiers = ['Framework :: Zope 3'],
    install_requires=[
        'setuptools',
        'python-ldap',
        'ZODB3',
        'zope.interface',
        'zope.component',
        'zope.schema',
        'zope.app.container',
        'zope.app.component',
        'zope.security',
        'zope.i18nmessageid',
    ],
    extras_require=dict(
        test=[
            'zope.testing',
        ])
    )

