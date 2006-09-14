from setuptools import setup, find_packages

name='zc.buildoutsftp'
setup(
    name=name,
    version = "0.1",
    author = "Jim Fulton",
    author_email = "jim@zope.com",
    description =
    "Specialized zc.buildout plugin to add sftp support.",
    long_description = (
        open('README.txt').read()
        + '\n' + 
        open('CHANGES.txt').read()
        ),
    license = "ZPL 2.1",
    keywords = "buildout",
    url='http://www.python.org/pypi/'+name,

    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['zc'],
    install_requires = ['paramiko', 'setuptools'],
    zip_safe=False,
    )

                      
