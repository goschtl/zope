import glob
import logging
import os, sys
import shutil
import urllib
import tempfile
from distutils import sysconfig

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
            'download-url',
            'ftp://ftp.snt.utwente.nl/pub/software/openoffice/stable/2.0.4/OOo_2.0.4_LinuxIntel_install.tar.gz')
        options.setdefault(
            'unpack-name',
            'OOD680_m5_native_packed-1_en-US.9073')

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
        if copy_created:
            self.hack_python()
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
        shutil.copytree(os.path.join(storage, 'opt', 'openoffice.org2.0'),
                        location)
        return True

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
