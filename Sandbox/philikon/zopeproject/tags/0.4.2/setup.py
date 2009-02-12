from setuptools import setup, find_packages

long_description = (open('README.txt').read() +
                    '\n\n' +
                    open('CHANGES.txt').read())

setup(
    name='zopeproject',
    version='0.4.2',
    author='Philipp von Weitershausen',
    author_email='philipp@weitershausen.de',
    url='http://cheeseshop.python.org/pypi/zopeproject',
    download_url='svn://svn.zope.org/repos/main/Sandbox/philikon/zopeproject/trunk#egg=zopeproject-dev',
    description='Tools and scripts for creating development sandboxes for '
                'web applications that primarily use Zope',
    long_description=long_description,
    license='ZPL',
    classifiers=['Environment :: Console',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: Zope Public License',
                 'Programming Language :: Python',
                 'Topic :: Internet :: WWW/HTTP :: WSGI',
                 'Framework :: Zope3',
                 ],

    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=['PasteScript>=1.3',],
    entry_points="""
    [console_scripts]
    zopeproject = zopeproject.main:zopeproject
    [paste.paster_create_template]
    zope_deploy = zopeproject.templates:ZopeDeploy
    zope_app = zopeproject.templates:ZopeApp
    """,
)
