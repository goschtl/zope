from setuptools import setup, find_packages

setup(name='z3c.zalchemy',
      version='trunk',
      author='Juergen Kartnaller',
      url='https://svn.zope.org.repos/main',
      description="""SQLAlchemy integration into Zope 3""",
      license='ZPL 2.1',

      packages=find_packages('src'),
      package_dir = {'': 'src'},
      include_package_data = True,
      zip_safe=False,
      install_requires=['setuptools',
                        'SQLAlchemy',
                        'ZODB3',
                        'zope.component',
                        'zope.interface',
                        'zope.schema',
                        'zope.app',
                       ],
      extras_require = dict(test=['pysqlite']))
