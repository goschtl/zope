from setuptools import setup, find_packages

setup(
    name='z3c.zalchemy',
    version='trunk',
    author='ROBOTECH???',
    url='https://svn.zope.org.repos/main',
    description="""\
SQLAlchemy integration into Zope 3
""",
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data = True,
    zip_safe=False,
    license='ZPT 2.1',
    install_requires=['setuptools',
                      'SQLAlchemy'],
)



