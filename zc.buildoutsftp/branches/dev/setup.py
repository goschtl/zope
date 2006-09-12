from setuptools import setup, find_packages

name='zc.buildoutsftp'
setup(
    name=name,
    version = "0.1",
    author = "Jim Fulton",
    author_email = "jim@zope.com",
    description =
    "Specialized urllib2 plugin for sftp for use in zc.buildout.",
    long_description = open('README.txt').read(),
    license = "ZPL 2.1",
    keywords = "buildout",
    url='http://www.python.org/pypi/'+name,

    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['zc'],
    install_requires = ['paramiko', 'setuptools'],
    tests_require = ['zope.testing'],
    test_suite = name+'.tests.test_suite',
    zip_safe=False,
    )

                      
