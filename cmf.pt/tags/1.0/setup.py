from setuptools import setup, find_packages

version = '1.0'

setup(name='cmf.pt',
      version=version,
      description="Bridge to use Chameleon with Zope 2 and CMF.",
      long_description=open("README.txt").read() + open("CHANGES.txt").read(),
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Programming Language :: Python",
        "Topic :: Text Processing :: Markup :: HTML",
        "Topic :: Text Processing :: Markup :: XML",
        ],
      keywords='',
      author='Malthe Borch and the Zope community',
      author_email='zope-dev@zope.org',
      url='',
      license='ZPL',
      namespace_packages=['cmf'],
      packages = find_packages('src'),
      package_dir = {'':'src'},
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'z3c.pt>=1.0b7',
          'five.pt',
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
