from setuptools import setup, find_packages

TINYMCE_VERSION = '2.6.0'

setup(
    name='hurry.tinymce',
    version=TINYMCE_VERSION + 'dev',
    description="tinymce for hurry.resource.",
    classifiers=[],
    keywords='',
    author='Martijn Faassen',
    author_email='faassen@startifact.com',
    license='ZPL 2.1',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['hurry'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'hurry.resource',
        ],
    entry_points= {
    'console_scripts': [
      'tinymceprepare = hurry.tinymce.prepare:main',
      ]
    },

    )
