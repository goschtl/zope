import os

from setuptools import setup, find_packages

version = '0.2'


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
        read('docs', 'README.txt') + '\n' +
        read('.', 'CHANGES.txt') + '\n' +
        read('docs', 'CREDITS.txt'))

setup(name='megrok.kss',
      version=version,
      description="KSS for Grok. Ajax with Style, see http://kssproject.org",
      long_description=long_description,
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
                        'grok>=0.13',
                        'kss.core>=1.4,<1.4.99',
                        # -*- Extra requirements: -*-
                        ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
