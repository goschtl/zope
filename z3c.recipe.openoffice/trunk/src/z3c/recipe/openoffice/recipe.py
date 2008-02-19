import glob
import logging
import os, sys
import shutil
import urllib
from distutils import sysconfig
import zc.buildout

PYUNO_SETUP = """
from setuptools import setup, find_packages
import sys, os

version = '0.1'

name='pyuno'

setup(name=name,
      version=version,
      author="Affinitic",
      author_email="jfroche@affinitic.be",
      description="little egg with pyuno",
      license='ZPL 2.1',
      keywords = "openoffice",
      url='http://svn.affinitic.be',
      packages=find_packages('src'),
      include_package_data=True,
      package_dir = {'': 'src'},
      namespace_packages=[],
      install_requires=['setuptools'],
      zip_safe=False)
"""

class Recipe(object):
    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options
        self.logger = logging.getLogger(self.name)

        options['location'] = os.path.join(
            buildout['buildout']['parts-directory'],
            self.name)
        python = buildout['buildout']['python']
        options['executable'] = buildout[python]['executable']

        options['tmp-storage'] = os.path.join(
            buildout['buildout']['directory'], 'tmp-storage')
        options.setdefault(
            'version','2.3')
        options.setdefault(
            'download-url',
            'ftp://ftp.openoffice.skynet.be/pub/ftp.openoffice.org/stable/2.3.0/OOo_2.3.0_LinuxIntel_install_en-US.tar.gz')
        options.setdefault(
            'unpack-name',
            'OOG680_m9_native_packed-1_en-US.9238')
        options.setdefault(
            'hack-openoffice-python',
            'no')
        options.setdefault(
            'install-pyuno-egg',
            'no')

    def install(self):
        location = self.options['location']
        if os.path.exists(location):
            return location
        storage = self.options['tmp-storage']
        if not os.path.exists(storage):
            os.mkdir(storage)
        download_file = self.download(storage)
        self.untar(download_file, storage)
        self.unrpm(storage)
        copy_created = self.copy(storage)
        if copy_created and \
           self.options['hack-openoffice-python'].lower() == 'yes':
            self.hack_python()
        if copy_created and self.options['install-pyuno-egg'].lower() == 'yes':
            self.install_pyuno_egg()
        return location

    def download(self, whereto):
        """Download tarball into temporary location.
        """
        url = self.options['download-url']
        tarball_name = os.path.basename(url)
        download_file = os.path.join(whereto, tarball_name)
        if not os.path.exists(download_file):
            self.logger.info(
                'Downloading %s to %s', url, download_file)
            urllib.urlretrieve(url, download_file)
        else:
            self.logger.info("Tarball already downloaded.")
        return download_file

    def untar(self, download_file, storage):
        """Untar tarball into temporary location.
        """
        unpack_dir = os.path.join(storage, self.options['unpack-name'])
        if os.path.exists(unpack_dir):
            self.logger.info("Unpack directory (%s) already exists... "
                             "skipping unpack." % unpack_dir)
            return
        self.logger.info("Unpacking tarball")
        os.chdir(storage)
        status = os.system('tar xzf ' + download_file)
        assert status == 0
        assert os.path.exists(unpack_dir)

    def unrpm(self, storage):
        """extract information from rpms into temporary locatin.
        """
        unrpm_dir = os.path.join(storage, 'opt')
        if os.path.exists(unrpm_dir):
            self.logger.info("Unrpm directory (%s) already exists... "
                             "skipping unrpm." % unrpm_dir)
            return
        self.logger.info("Unpacking rpms")
        os.chdir(storage)
        unpack_dir = os.path.join(storage, self.options['unpack-name'])
        for path in glob.glob(os.path.join(unpack_dir, 'RPMS', '*.rpm')):
            os.system('rpm2cpio %s | cpio -idum' % path)

    def copy(self, storage):
        """Copy openoffice installation into parts directory.
        """
        location = self.options['location']
        if os.path.exists(location):
            self.logger.info('No need to re-install openoffice part')
            return False
        self.logger.info("Copying unpacked contents")
        shutil.copytree(os.path.join(storage, 'opt', 'openoffice.org%s' % self.options['version']),
                        location)
        return True

    def install_pyuno_egg(self):
        self.logger.info("Creating pyuno egg")
        location = self.options['location']
        program_dir = os.path.join(location, 'program')
        fd = open(os.path.join(program_dir,'setup.py'), 'w')
        fd.write(PYUNO_SETUP)
        fd.close()
        egg_src_dir = os.path.join(program_dir,'src')
        if not os.path.isdir(egg_src_dir):
            os.mkdir(egg_src_dir)
        for filename in ['pyuno.so', 'uno.py']:
            if not os.path.islink(os.path.join(egg_src_dir,filename)):
                os.symlink(os.path.join(program_dir,filename),
                           os.path.join(egg_src_dir,filename))
        eggDirectory = self.buildout['buildout']['eggs-directory']
        zc.buildout.easy_install.develop(program_dir, eggDirectory)

    def hack_python(self):
        """Hack a different python into the OpenOffice installation.

        This is so we can use UNO from that Python.

        Right now we're hacking the same Python into OpenOffice as the
        one used to run buildout with.
        """
        self.logger.info("Hacking python into openoffice")
        location = self.options['location']
        program_dir = os.path.join(location, 'program')
        os.remove(os.path.join(program_dir, 'libpython2.3.so.1.0'))
        shutil.rmtree(os.path.join(program_dir, 'python-core-2.3.4'))
        os.remove(os.path.join(program_dir, 'pythonloader.unorc'))
        
        pythonhome = sys.exec_prefix
        pythonpath = sysconfig.get_python_lib(standard_lib=True)
        so = os.path.join(
            os.path.split(pythonpath)[0],
            'libpython%s.so.1.0' % sys.version[:3])
        os.symlink(so, os.path.join(program_dir, 'libpython2.3.so.1.0'))
        f = open(os.path.join(location, 'program', 'pythonloader.unorc'), 'w')
        f.write('''\
[Bootstrap]
PYTHONHOME=file://%s
PYTHONPATH=%s $ORIGIN
''' % (pythonhome, pythonpath))
        f.close()

    def update(self):
        pass
