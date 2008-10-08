from setuptools import setup, find_packages

setup(
    name='talk.z3cform',
    version='0.1.0dev',
    author='Trainee',
    author_email='zope-dev@zope.org',
    description='Zope 3 Talk: Z3C Forms',
    long_description='Zope 3 Talk: Z3C Forms',
    license='ZPL 2.1',
    keywords='zope3 talk z3cform',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope3'],
    url='http://pypi.python.org/pypi/talk.z3cform',
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['talk'],
    extras_require = dict(
        app = [
            'ZODB3',
            'ZConfig',
            'zdaemon',
            'zope.publisher',
            'zope.traversing',
            'zope.app.wsgi',
            'zope.app.appsetup',
            'zope.app.zcmlfiles',
            'zope.app.securitypolicy',
            'zope.app.twisted',
            # APIDOC packages
            'zope.app.apidoc',
            'zope.app.preference',
            'zope.app.onlinehelp',
            # The following packages aren't needed from the
            # beginning, but end up being used in most apps
            'zope.annotation',
            'zope.copypastemove',
            'zope.i18n',
            'zope.app.authentication',
            'zope.app.session',
            'zope.app.intid',
            'zope.app.keyreference',
            'zope.app.catalog',
            ],
        test = [
            'zope.testbrowser',
            'zope.app.testing'],
        ),
    install_requires = [
        'setuptools',
        'z3c.csvvocabulary',
        'z3c.form',
        'z3c.formui',
        ],
    zip_safe = False,
    )
