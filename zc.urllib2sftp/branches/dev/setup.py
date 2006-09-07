from setuptools import setup

name='zc.urllib2sftp'
setup(
    name=name,
    version = "1.0.0a3",
    author = "Jim Fulton",
    author_email = "jim@zope.com",
    description = "urllib2 plugin for sftp.",
    long_description = open('README.txt').read(),
    license = "ZPL 2.1",
    keywords = "sftp",
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

                      
