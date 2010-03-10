from setuptools import setup, find_packages

version = '0.5'

setup(name='megrok.rendersource',
      version=version,
      description="Grok source renderers",
      long_description="""\
""",
      classifiers=[], 
      keywords="",
      author="d2m",
      author_email="michael@d2m.at",
      url="",
      license="ZPL",
      package_dir={'': 'src'},
      namespace_packages=['megrok'],      
      packages=find_packages('src'),
      include_package_data=True,
      zip_safe=False,
      extras_require={'test': [
          'zope.app.testing',
          'zope.testbrowser',
          'zope.app.zcmlfiles',
          'zope.securitypolicy',
          'zope.app.authentication',
          ]},
      install_requires=['setuptools',
                        'grokcore.view',
                        # -*- Extra requirements: -*-
                        ],
      entry_points = """
      """,
       )
