from setuptools import setup, find_packages

setup(
    name="zc.i18n",
    version="0.5.1",
    packages=find_packages('src', exclude=["*.tests", "*.ftests"]),
    
    package_dir= {'':'src'},
    
    namespace_packages=['zc'],
    package_data = {
    '': ['*.txt', '*.zcml'],
    },

    zip_safe=False,
    author='Zope Project',
    author_email='zope3-dev@zope.org',
    description="""\
zc.i18n contains a i18n related helper code.
""",
    license='ZPL',
    keywords="zope zope3",
    )
