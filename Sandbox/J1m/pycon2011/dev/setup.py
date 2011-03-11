from setuptools import setup
setup(
    name = 'cmsapp',
    py_modules = ['cmsapp'],
    install_requires = ['setuptools', 'bobo', 'ZODB3'],
    zip_safe = False,
    )
