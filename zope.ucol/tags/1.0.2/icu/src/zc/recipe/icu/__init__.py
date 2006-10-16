import os, sys, shutil, tempfile, urllib2
import setuptools.archive_util

class Recipe:

    def __init__(self, buildout, name, options):
        self.name = name
        self.options = options
        self.location = os.path.join(
            buildout['buildout']['parts-directory'],
            self.name)
        options['location'] = self.location
        if sys.platform.startswith('linux'):
            platform = 'LinuxRedHat'
        elif sys.platform.startswith('darwin'):
            platform = 'MacOSX'
        elif sys.platform.startswith('win32'):
            platform = 'win32'
        else:
            raise SystemError("Can't guess an ICU platform")
        options['platform'] = platform

    def install(self):
        options = self.options
        dest = options['location']
        if os.path.exists(dest):
            return dest

        if options['platform'] == 'win32':
            return self.install_win32(options, dest)
        
        here = os.getcwd()
        tmp = tempfile.mkdtemp()
        try:
            f = urllib2.urlopen(
                'ftp://ftp.software.ibm.com/software/globalization/icu/'
                '%(version)s/icu-%(version)s.tgz'
                % dict(version=options['version'])
                )
            open(os.path.join(tmp, 'arch'), 'w').write(f.read())
            f.close()
            setuptools.archive_util.unpack_archive(
                os.path.join(tmp, 'arch'),
                tmp,
                )
            os.chdir(os.path.join(tmp, 'icu', 'source'))
            assert os.spawnl(
                os.P_WAIT, 
                os.path.join(tmp, 'icu', 'source', 'runConfigureICU'),
                os.path.join(tmp, 'icu', 'source', 'runConfigureICU'),
                options['platform'],
                '--prefix='+dest,
                ) == 0
            assert os.spawnlp(os.P_WAIT, 'make', 'make', 'install') == 0
        finally:
            os.chdir(here)
            shutil.rmtree(tmp)

        return dest

    def update(self):
        pass

    def install_win32(self, options, dest):
        tmp = tempfile.mkstemp()
        try:
            f = urllib2.urlopen(
                'ftp://ftp.software.ibm.com/software/globalization/icu/'
                '%(version)s/icu-%(version)s-Win32-msvc7.1.zip'
                % dict(version=options['version'])
                )
            open(tmp, 'w').write(f.read())
            f.close()
            setuptools.archive_util.unpack_archive(tmp, dest)
        finally:
            shutil.rmfile(tmp)

        return dest
        
