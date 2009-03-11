from setuptools import setup, find_packages
import os

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

#long_description = (
#    read('src/hurry/file/README.txt')
#    + '\n' +
#    read('src/hurry/file/browser/file.txt')
#    + '\n' + 
#    read('CHANGES.txt')
#    )

setup(
    name="hurry.filesize",
    version="09ev",
    description="""\
hurry.filesize is a simple Python library to make display human readable
sizes of files (or anything that is sized in bytes), in kilobytes, megabytes,
etc.
""",
#    long_description=long_description,
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
    keywords='file size bytes',
    author='Martijn Faassen, Startifact',
    author_email='faassen@startifact.com',
    url='',
    license='ZPL 2.1',
    packages=find_packages('src'),
    package_dir= {'':'src'},
    namespace_packages=['hurry'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
       'setuptools',
       ],
    )
