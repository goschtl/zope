from setuptools import setup, find_packages

setup(
    name='i18nmigrate',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'zope.i18n',
        'zope.app.locales',
        'python-gettext',
    ],
    entry_points={
        'console_scripts': [
            'makecatalog = i18nmigrate:makecatalog'
        ]
    }
)
