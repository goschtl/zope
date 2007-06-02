from setuptools import setup, find_packages

setup(name='z3c.evalexception',
      version = '1.0',
      license='ZPL 2.1',
      description="Paste's interactive exception debugger for Zope 3",
      author='Philipp von Weitershausen',
      author_email='philipp@weitershausen.de',
      long_description=open('README.txt').read(),
      packages=find_packages(),
      namespace_packages=['z3c'],
      install_requires=['setuptools', 'Paste'],
      zip_safe=True,
      entry_points="""
      [paste.filter_app_factory]
      main = z3c.evalexception:zope_eval_exception
      """
      )
