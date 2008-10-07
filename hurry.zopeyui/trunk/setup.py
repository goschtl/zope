from setuptools import setup, find_packages
import sys, os, shutil
import yuidl

YUI_VERSION = '2.6.0'

package_dir = os.path.dirname(__file__)
yui_build_path = os.path.join(package_dir, 'src', 'hurry', 'zopeyui',
                              'yui-build')

def copy_yui(ex_path):
    """Copy YUI to location 'yui-build' in package."""
    yui_build_path = os.path.join(ex_path, 'yui', 'build')
    shutil.rmtree(target_path, ignore_errors=True)
    shutil.copytree(yui_build_path, yui_build_path)

# only re-download if path doesn't exist
if not os.path.exists(yui_build_path):
    yuidl.download(YUI_VERSION, copy_yui)

setup(
    name='hurry.zopeyui',
    version='0.1dev',
    description="Zope integration for YUI.",
    classifiers=[],
    keywords='',
    author='Martijn Faassen',
    author_email='faassen@startifact.com',
    license='ZPL 2.1',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'hurry.zoperesource',
        'hurry.yui',
        ],
    )
