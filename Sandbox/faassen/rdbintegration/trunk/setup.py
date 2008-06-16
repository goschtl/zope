from setuptools import setup, find_packages

setup(name='rdbintegration',
      version="0.1",
      description="An SQLAlchemy integration experiment",
      classifiers=[], 
      author="Martijn Faassen",
      author_email="faassen@startifact.com",
      license="ZPL",
      package_dir={'': 'src'},
      packages=find_packages('src'),
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'grok',
                        'SQLAlchemy == 0.5beta1',
                        'zope.sqlalchemy',
                        'psycopg2',
                        # Add extra requirements here
                        ],
      entry_points="""
      # Add entry points here
      """,
      )
