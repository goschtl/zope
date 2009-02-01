from setuptools import setup, find_packages

setup(
    name='zopesandbox',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    include_package_data=True,
    install_requires=[
        'zope.app.zcmlfiles',
        'zope.app.authentication',
        'zope.app.securitypolicy',
        'zope.app.catalog',
        'zope.app.twisted',
        'zope.app.undo',
        'zope.app.apidoc',
        'zope.app.homefolder',
        'zope.app.file',
        'zope.sendmail',
        'zope.viewlet',
    ],
)
