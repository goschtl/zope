from setuptools import setup, find_packages

version = '0.1'

setup(name='megrok.simpleauth',
      version=version,
      description="Simple authentication setup for Grok apps.",
      long_description="""\
Simple authentication setup for Grok apps.""",
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='grok authentication',
      author='Leonardo Rochael, Luciano Ramalho, Rodrigo Pimentel',
      author_email='',
      url='',
      license='ZPL',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['megrok'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
