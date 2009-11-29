from setuptools import setup, find_packages

version = '0.2'

setup(name='z3c.deadlockdebugger',
      version=version,
      description="A thread debugger.",
      long_description=open("README.txt").read() + open("CHANGES.txt").read(),
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',
      url='http://svn.zope.org/z3c.deadlockdebugger',
      license='ZPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['z3c'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'zope.publisher',
          'threadframe',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
