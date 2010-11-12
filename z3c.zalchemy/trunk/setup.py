import os
from setuptools import setup, find_packages

setup(name='z3c.zalchemy',
      version='0.3dev',
      author='Juergen Kartnaller and the Zope Community',
      author_email='zope3-dev@zope.org',
      url='http://pypi.python.org/pypi/z3c.sqlalchemy',
      description="""SQLAlchemy integration into Zope 3""",
      long_description=(file(
          os.path.join(os.path.dirname(__file__),
                       'src', 'z3c', 'zalchemy', 'README.txt')).read() +
          '\n\n' +
          file(os.path.join(os.path.dirname(__file__), 'CHANGES.txt')).read()),

      license='ZPL 2.1',

      packages=find_packages('src'),
      package_dir = {'': 'src'},
      include_package_data = True,
      zip_safe=False,
      install_requires=['setuptools',
                        'SQLAlchemy>=0.4.3',
                        'ZODB3',
                        'zope.app.component',
                        'zope.app.container',
                        'zope.app.keyreference',
                        'zope.app.pagetemplate',
                        'zope.app.testing',
                        'zope.component',
                        'zope.deferredimport',
                        'zope.interface',
                        'zope.schema',
                       ],
      extras_require = dict(test=['pysqlite']))
