from setuptools import setup, find_packages
import sys, os, shutil, tempfile

EXTJS_VERSION = '2.2.1'

extzip = os.path.expanduser('~') + '/ext-%s.zip' % EXTJS_VERSION

dirpath = tempfile.mkdtemp()
extjs_path = os.path.join(dirpath, 'extjs.zip')
ex_path = os.path.join(dirpath, 'extjs_ex')

shutil.copy(extzip, extjs_path)
os.system('unzip -qq "%s" -d "%s"' % (extjs_path, ex_path))

package_dir = './src/hurry/extjs/'
dest_path = os.path.join(package_dir, 'extjs-build')

# remove previous ExtJS
shutil.rmtree(dest_path, ignore_errors=True)

build_path = os.path.join(ex_path)
shutil.copytree(build_path, dest_path)

shutil.rmtree(dirpath, ignore_errors=True)

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.txt')
    + '\n' +
    read('CHANGES.txt')
    + '\n' +
    'Download\n'
    '********\n'
    )

setup(
    name='hurry.extjs',
    version=EXTJS_VERSION,
    description="ExtJS for hurry.resource.",
    long_description=long_description,
    classifiers=[],
    keywords='',
    author='Santiago Videla',
    author_email='santiago.videla@gmail.com',
    license='ZPL 2.1',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['hurry'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'hurry.resource',
        ],
    entry_points= {
    },

    )
