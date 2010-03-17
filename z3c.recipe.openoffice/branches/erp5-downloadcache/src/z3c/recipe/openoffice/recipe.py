import glob
import logging
import os, sys
import shutil
from distutils import sysconfig
import zc.buildout.easy_install
import zc.buildout.download
from platform import uname

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

BASE_URL = ('http://download.services.openoffice.org/files/stable/3.2.0/'
            'OOo_3.2.0_Linux%s_install_wJRE_en-US.tar.gz')
# XXX add more rpm platforms (HPPA, IA64, S390X, PPC)
ARCH_MAP = {
    'i386': 'Intel',
    'i586': 'Intel',
    'i686': 'Intel',
    'x86_64': 'X86-64'
}
DEFAULT_UNPACK_NAME = 'OOO320_m12_native_packed-1_en-US.9483'
DEFAULT_VERSION = '3'

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

        options.setdefault('tmp-storage', options['location'] + '__unpack__')
        if not options.get('download-url'):
            base_url = options.setdefault('base-url', BASE_URL)
            options.setdefault('platform', self._guessPackagePlatform())
            options['download-url'] = base_url % options['platform']
        options.setdefault(
            'hack-openoffice-python',
            'no')
        options.setdefault(
            'install-pyuno-egg',
            'no')

        # XXX: these two settings below are mere package layout details
        # that the user should not be bothered with. We should simply be
        # smarter about looking inside the package and figuring out this
        # information.
        options.setdefault('version', DEFAULT_VERSION)
        options.setdefault('unpack-name', DEFAULT_UNPACK_NAME)

    def _guessPackagePlatform(self):
        arch = uname()[-2]
        target = ARCH_MAP.get(arch)
        assert target, 'Unknown architecture'
        return target

    def install(self):
        location = self.options['location']
        if os.path.exists(location):
            return location
        storage = self.options['tmp-storage']
        if not os.path.exists(storage):
            os.mkdir(storage)
        download_file, is_temp = self.download()
        self.untar(download_file, storage)
        if is_temp:
            os.remove(download_file)
        self.unrpm(storage)
        copy_created = self.copy(storage)
        if (copy_created and
            self.options['hack-openoffice-python'].lower() == 'yes'):
            self.hack_python()
        if copy_created and self.options['install-pyuno-egg'].lower() == 'yes':
            self.install_pyuno_egg()
        # XXX, actually remove the "temporary" storage. It's not very temporary
        # right now...
        return [location, storage]

    def download(self):
        """Download tarball. Caching if required.
        """
        url = self.options['download-url']
        namespace = self.options['recipe']
        download = zc.buildout.download.Download(self.buildout['buildout'],
                                                 namespace=namespace,
                                                 logger=self.logger)
        return download(url)

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
        # avoiding internal tarfile module for now, due to the python 2.4 bug
        # http://bugs.python.org/issue1509889
        status = os.system('tar xzf ' + download_file)
        assert status == 0
        assert os.path.exists(unpack_dir), ("Package did not unpack to '%s'" %
                                            unpack_dir)

    def unrpm(self, storage):
        """extract information from rpms into temporary location.
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
