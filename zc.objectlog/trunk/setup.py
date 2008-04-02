from setuptools import setup, find_packages

long_description = open("src/zc/objectlog/log.txt").read()

setup(
    name="zc.objectlog",
    version="0.1",
    license="ZPL 2.1",
    author="Zope Corporation",
    author_email="zope-dev@zope.org",
    description=open('README.txt').read(),
    long_description=long_description,
    keywords="zope zope3 logging",
    packages=find_packages('src'),
    package_dir={'':'src'},
    namespace_packages=['zc'],
    include_package_data=True,
    install_requires = [
        'setuptools',
        'zc.copy',
        'zc.security',
        'zope.app.keyreference',
    ],
    zip_safe = False
    )
