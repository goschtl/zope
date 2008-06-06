from setuptools import setup, find_packages

setup(
    name='classix',
    version='0.1',
    author='Martijn Faassen',
    author_email='faassen@startifact.com',
    description="""\
Declarative way to associate classes with lxml XML elements.
""",
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data = True,
    zip_safe=False,
    install_requires=[
    'setuptools',
    'lxml == 2.0.6',
    'martian >= 0.10',
    ],
)
