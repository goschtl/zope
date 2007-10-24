from setuptools import setup
setup(
    name='zc.sourcerelease.sample', version=1,
    url='http://www.zope.org', author='bob', author_email='bob@foo.com',
    py_modules = ['zc_sourcerelease_sample_script'],
    entry_points = {'console_scripts':
                    ['sample=zc_sourcerelease_sample_script:main']},
    )
