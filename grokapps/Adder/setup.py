from setuptools import setup, find_packages

version = '0.0'

setup(name='Adder',
      version=version,
      description="",
      long_description="",
      classifiers=[], 
      keywords="",
      author="",
      author_email="",
      url="",
      license="",
      package_dir={'': 'src'},
      packages=find_packages('src'),
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'grok',
                        'grokui.admin',
                        'z3c.testsetup',
                        'zope.app.file',
                        ],
      entry_points="",
)
