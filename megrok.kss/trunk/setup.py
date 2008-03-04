from setuptools import setup, find_packages

version = '0.1'

setup(name='megrok.kss',
      version=version,
      description="KSS for Grok.",
      long_description="""\
""",
      classifiers=[], 
      keywords="",
      author="Godefroid Chapelle",
      author_email="gotcha@bubblenet.be",
      url="",
      license="ZPL",
      package_dir={'': 'src'},
      namespace_packages=['megrok'],      
      packages=find_packages('src'),
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'grok',
                        'kss.core>=1.4,<1.5',
                        # -*- Extra requirements: -*-
                        ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
