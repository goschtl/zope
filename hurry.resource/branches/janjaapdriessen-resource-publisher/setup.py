from setuptools import setup, find_packages
import os

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('src', 'hurry', 'resource', 'README.txt')
    + '\n' +
    read('CHANGES.txt')
    + '\n' +
    'Download\n'
    '********\n'
    )

setup(
    name='hurry.resource',
    version='0.11dev',
    description="Flexible resources for web applications.",
    long_description=long_description,
    classifiers=[],
    keywords='',
    author='Martijn Faassen',
    author_email='faassen@startifact.com',
    license='ZPL 2.1',
    url='http://pypi.python.org/pypi/hurry.resource',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['hurry'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        ],
    extras_require = dict(publisher=['Paste'],
                          test=['Paste', 'WebOb', 'zc.buildout'],
                          wsgi=['WebOb']),
    entry_points = {
        'paste.app_factory': [
            'publisher = hurry.resource.publisher:make_publisher'],
        'paste.filter_app_factory': [
            'inject = hurry.resource.wsgi:make_inject'],
    })
