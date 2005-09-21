##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
import ConfigParser
import errno
import getpass
import os
import os.path
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib
import urlparse
import zipfile

verbose = 0 # set by buildout.py

# Capture the base path of the buildout.

__base_path = os.path.abspath('.')
def getBasePath():
    return __base_path

def getBuildPath(name):
    if name not in dict(getPackages()):
        raise RuntimeError(
            'Package "%s" is unknown, can\'t get its build prefix.' % package)

    path = queryOption(name, 'prefix')
    if path is None:
        path = os.path.join('var', 'opt', name)
    else:
        path = os.path.expanduser(path)

    if os.path.isabs(path):
        return path
    else:
        return os.path.join(getBasePath(), path)

def isExternal(name):
    result = bool(queryOption(name, 'prefix'))
    if sys.platform.startswith('win'):
        if result and name != 'python':
            raise RuntimeError('External packages (other than Python) are '
                               'not supported on Windows.')
        elif not result and name == 'python':
            raise RuntimeError('On Windows Python must be external.')
    return result

def getPathToBinary(name):
    path = queryOption(name, 'binary')
    if path is None:
        raise RuntimeError('There is no binary defined for "%s".' % name)

    path = os.path.expanduser(queryOption(name, 'binary'))
    if os.path.isabs(path):
        return path
    else:
        return os.path.join(getBasePath(), path)

_packages = None

def getPackages():
    """Return a list of packages to build.

    Each package is specified as a (name, version) pair.  Name is a
    string, and version is a string or None.
    """
    global _packages
    if _packages is not None:
        return _packages
    fn = os.path.join(getBasePath(), "buildout/config.ini")
    cp = ConfigParser.SafeConfigParser()
    cp.readfp(open(fn))

    def lookup(group, option, default=None):
        platkey = "%s:%s" % (group, sys.platform)
        if cp.has_option(platkey, option):
            return cp.get(platkey, option)
        if cp.has_option(group, option):
            return cp.get(group, option)
        return default

    _packages = [(name, lookup("versions", name))
                 for name in lookup("buildout", "packages").split()]
    return _packages

def getVersion(name):
    return dict(getPackages())[name]

_config = None
def getConfiguration():
    global _config
    if _config is None:
        _config = ConfigParser.SafeConfigParser()
        fn = os.path.join(getBasePath(), "buildout.ini")
        if not os.path.exists(fn):
            f = open(fn, 'wt')
            print >>f, "; configuration file for this buildout"
            print >>f
            print >>f, "; Set the username to use in SSH authentication using"
            print >>f, "; the 'username' setting in a section with the same"
            print >>f, "; name as the host for which authentication is needed."
            print >>f
            print >>f, "[svn.zope.com]"
            print >>f, "username =", getpass.getuser()
            print >>f
            print >>f, "[svn.zope.org]"
            print >>f, "username ="
            print >>f
            print >>f, "[configure]"
            print >>f, "; the file name to use for \"configure\" cache"
            print >>f, "cache_file = var/config.cache"
            print >>f
            print >>f, "[python]"
            print >>f, "; the path to the Python build (if not being built)"
            if sys.platform.startswith('win'):
                print >>f, "prefix = c:\\python24"
            else:
                print >>f, ";prefix = some/path/to/python"
            print >>f
            print >>f, "; the path to the Python binary, change if using an"
            print >>f, "; external Python"
            if sys.platform.startswith('win'):
                print >>f, "binary = c:\\python24\\python.exe"
            else:
                print >>f, "binary = var/opt/python/bin/python"
            print >>f
            print >>f, "; example of using external package instead of"
            print >>f, "; building from scratch"
            print >>f, ";[libxml2]"
            print >>f, ";prefix = /some/path/to/libxml2"

            f.close()
        _config.readfp(open(fn))
    return _config

def queryOption(group, option):
    try:
        return getConfiguration().get(group, option)
    except ConfigParser.NoSectionError:
        return None
    except ConfigParser.NoOptionError:
        return None

def getSourcePath(package):
    if package not in dict(getPackages()):
        raise RuntimeError('Package "%s" is unknown, can\'t get its source.'
                           % package)

    return os.path.join(getBasePath(), 'var', 'src', package)

def getBaseArchivePath():
    return os.path.join(getBasePath(), 'var', 'files')

DOT_TIME = 0.33
last_activity_dot_time = 0
def activityDot():
    global last_activity_dot_time
    if verbose == 0 and time.time() - last_activity_dot_time > DOT_TIME:
        sys.stdout.write('.')
        sys.stdout.flush()
        last_activity_dot_time = time.time()

def runCommand(file, args=(), successMarker=None, errorMarker=None,
               ignoreExitCode=False):
    if verbose >= 2:
        print 'buildout: executing ', file, ' '.join(args)

    command = [file]
    command.extend(args)
    child = subprocess.Popen(command, stdout=subprocess.PIPE, 
                             stderr=subprocess.STDOUT)

    output = []
    while True:
        activityDot()
        output.append(child.stdout.read())
        if child.poll() is not None:
            break
        time.sleep(0)

    output = ''.join(output)
    try:
        if not (successMarker or errorMarker):
            # If no success or error text was provided, use the proccess'
            #  exit value.
            if child.returncode and not ignoreExitCode:
                raise RuntimeError('Command exit code indicated error: '+
                                   ' '.join(command))
        else:
            if errorMarker != None and errorMarker in output:
                raise RuntimeError('Command produced erronious output.')
            if successMarker != None and successMarker not in output:
                raise RuntimeError('Command failed to produce success output.')
    except:
        print output
        raise

    if verbose >= 3:
        print output

    return output

packagePaths = []
def registerPythonPackage(path):
    packagePaths.append(path)

def setUpPackages():
    mkdir('var/opt')
    pathToPaths = 'var/opt/paths'
    try:
        path_file = open(pathToPaths, 'rt')
    except IOError, e:
        if e.errno == errno.ENOENT: # the file doesn't exist
            paths = []
        else:
            raise
    else:
        paths = [line.rstrip() for line in path_file.readlines()]
        path_file.close()

    path_file = open(pathToPaths, 'at')
    for new_path in packagePaths:
        if new_path not in paths:
            path_file.write(new_path)
            path_file.write('\n')
            paths.append(new_path)
    path_file.close()

def svnCheckout(url, path):
    runCommand('svn', ['checkout', url, path])

def svnUpdate(name):
    svnUpdatePath(getSourcePath(name))

current_repo_versions = {}
def svnUpdatePath(path):
    chdir(path)
    uuid, current_revision = getSubversionInfo(path)
    if current_repo_versions.get(uuid, 999999999) > current_revision:
        # if something has changed in this part of the repo, update it
        log_xml = runCommand('svn', ['log', '-r', 'BASE:HEAD', '--xml'])
        match = re.search(r'<logentry[^>]+revision="(\d+)"', log_xml, re.S)
        if match:
            last_revision = int(match.group(1))
        else:
            last_revision = 999999999

        if '<log>\n</log>' in log_xml or last_revision == current_revision:
            if verbose > 0:
                print 'buildout: skipping "%s" (nothing has changed)' % path
        else:
            if verbose > 0:
                print 'buildout: updating "%s"' % path

            output = runCommand('svn', ['update'])
            uuid, current_revision = getSubversionInfo(path)
            current_repo_versions[uuid] = current_revision
    else:
        if verbose > 0:
            print 'buildout: skipping "%s" (already up to date)' % path
    popdir()

def getSubversionInfo(path):
    chdir(path)
    # collect some info about the working directory
    output = runCommand('svn', ('info',))

    # get the UUID of the repository
    match = re.search('^Repository UUID: (.*)$', output, re.MULTILINE)
    uuid = match.group(1)

    # get the current revision of the working directory
    match = re.search('^Revision: (.*)$', output, re.MULTILINE)
    current_revision = int(match.group(1))
    popdir()

    return uuid, current_revision

dir_stack = []
def chdir(path):
    if verbose > 1 and path != '.':
        print 'buildout: changing to directory', path
    dir_stack.append(os.getcwd())
    os.chdir(path)
    return dir_stack[-1]

def popdir():
    path = dir_stack.pop()
    if verbose > 1 and os.getcwd() != path:
        print 'buildout: changing to directory', path

    os.chdir(path)

def mkdir(path):
    try:
        os.makedirs(path, 0700)
    except OSError, e:
        if e.errno != errno.EEXIST: # file exists
            raise

def unlink(path):
    try:
        os.unlink(path)
    except OSError, e:
        if e.errno != errno.ENOENT: # no such file or directory
            raise

def rmtree(path):
    try:
        if sys.platform.startswith('win'):
            # the "rmdir" command complains if the path is already gone
            if os.path.exists(path):
                runCommand('rmdir', ['/q/s', os.path.normpath(path)])
        else:
            shutil.rmtree(path)
    except OSError, e:
        if e.errno != errno.ENOENT: # no such file or directory
            raise

def linkOrCopy(source, target):
    """Either symlink or copy one file to another, depending on OS.

    Source must be relative to the root of the buildout, and target must
    be relative to the source.
    """
    if sys.platform.startswith('win'):
        # because symlink and copy work differently, we have to massage the
        # target path a bit
        source = source.replace('../', '')
        if os.path.isdir(source):
            rmtree(target)
            shutil.copytree(source, target, True)
        else:
            unlink(target)
            shutil.copy(source, target)
    else:
        try:
            os.unlink(target)
        except OSError:
            # must not have been there
            pass

        os.symlink(source, target)
        
def dirBuildHelper(destination, func):
    if not os.path.exists(destination):
        error = False
        mkdir(destination)
        chdir(destination)
        try:
            try:
                func()
            except:
                error = True
        finally:
            popdir()

        if error:
            if os.path.exists(destination):
                chdir('..') # just in case we're *in* the direcory to be deleted
                shutil.rmtree(destination)
                popdir()
            raise

def getSource(name, url, user=None, unarchived_name=None):
    archive_name = fileFromUrl(url)
    destination = getSourcePath(name)

    def doDownload():
        if url.startswith('svn:') or url.startswith('svn+ssh:'):
            subversionGetSource(destination, name, url, user)
        elif url.startswith('http:') or url.startswith('ftp:'):
            urlGetSource(name, url, unarchived_name)
        else:
            raise RuntimeError('Unrecognized address scheme.')

    dirBuildHelper(destination, doDownload)

    return destination

def createFile(path, data, mode):
    mkdir(os.path.dirname(path))
    file = open(path, 'wb')
    file.write(data)
    file.close()
    os.chmod(path, mode)

def extract(archive_path, dir=None):
    if zipfile.is_zipfile(archive_path):
        file = zipfile.ZipFile(archive_path)
    elif tarfile.is_tarfile(archive_path):
        file = tarfile.TarFileCompat(archive_path, "r", tarfile.TAR_GZIPPED)
    else:
        raise RuntimeError('Unknown archive type: %s (perhaps the wrong thing '
                           'was downloaded, like a 404 page)' % archive_path)

    if dir is None:
        dir = tempfile.mktemp()
    mkdir(dir)
    for info in file.infolist():
        if info.filename[-1] != '/':
            data = file.read(info.filename)
            mode = getattr(info, 'mode', 0664)
            createFile(os.path.join(dir, info.filename), data, mode)
    return dir

def getFile(url, destination):
    file_name = fileFromUrl(url)
    if not os.path.exists(destination):
        try:
            def reporter(block, block_size, total_size):
                left = total_size - block * block_size
                sys.stderr.write('\r')
                sys.stderr.write('Downloading %s: ' % file_name)
                if left > 0: # the estimate is a bit rough, so we fake it a bit
                    sys.stderr.write('%sK left.' % (left/1024))
                else:
                    sys.stderr.write('done.')

                # it's possible that this line is shorter than the earlier one,
                # so we need to "erase" any leftovers
                sys.stderr.write(' '*10)
                sys.stderr.write('\b'*10)

            urllib.urlretrieve(url, destination, reporter)
            sys.stderr.write('\n')
        except: # bare except is ok, exception re-raised below
            if os.path.exists(destination):
                os.unlink(destination)
            raise

    # check to make sure we *really* got an executable
    if file_name.endswith('.exe'):
        f = open(destination)
        if f.read(2) != 'MZ': # Windows (and DOS) executables have this marker
            raise RuntimeError('Download of "%s" resulted in something that '
                'isn\'t an executable (perhaps a 404?).' % url)
        f.close()

    
def fileFromUrl(url):
    parts = urlparse.urlsplit(url)
    return parts[2].split('/')[-1]

def getArchive(url):
    mkdir(getBaseArchivePath())
    file_name = fileFromUrl(url)
    file_path = os.path.join(getBaseArchivePath(), file_name)
    getFile(url, file_path)
    return file_path

def urlGetSource(name, url, unarchived_name):
    # figure out from the passed in URL what the file's name should be
    file_path = getArchive(url)
    # extract the archive into a temp directory
    temp_dir = extract(file_path)

    # we are in the source directory, which we will replace, so get out
    chdir(getBasePath())

    # remove the out-of-date build directory
    if os.path.exists(getBuildPath(name)):
        shutil.rmtree(getBuildPath(name))

    # remove the out-of-date source directory
    if os.path.exists(getSourcePath(name)):
        shutil.rmtree(getSourcePath(name))

    # if the archive consists only of a single, top-level directory...
    if unarchived_name:
        # move the contents of the archive into the source directory
        shutil.move(os.path.join(temp_dir, unarchived_name),
                    getSourcePath(name))
    popdir()

def subversionGetSource(destination, name, url, user=None):
    # Remove the protocal because we want people to be able to pass in a
    #  user name and have a "svn://" url turn into a "svn+ssh://" url.
    url = url[url.index('/')+2:]
    if not url.endswith('/'):
        url += '/'

    if user:
        url = 'svn+ssh://%(user)s@%(url)s' % locals()
    else:
        url = 'svn://%(url)s' % locals()

    chdir(os.path.dirname(destination))
    svnCheckout(url, os.path.split(destination)[-1])
    popdir()

def distutilsCommand(name, command):
    source = getSourcePath(name)
    prefix = getBuildPath(name)

    def doit():
        os.chdir(source)
	runCommand(getPathToBinary('python'), 
                   ['setup.py', command, '--home', prefix])

    dirBuildHelper(prefix, doit)
    registerPythonPackage(os.path.join(prefix, 'lib', 'python'))

###############################################################################
### Recipe mix-ins

class DownloadSource(object):
    """Mix-in that downloads and unpacks source archives from the Internet

    The instance is required to have these attributes:

        self.name - the package name (e.g.  pyxml)
        self.download_url - the url from which to fetch the archive
        self.unarchived_name - the name of the top-level directory into which
                the archive will expand (may be None)
    """

    def get(self):
        site = urlparse.urlparse(
                    self.download_url[self.download_url.index(':')+1:])[1]
        user = queryOption(site, 'username')
        getSource(name=self.name, url=self.download_url,
                  unarchived_name=getattr(self, 'unarchived_name', None), 
                  user=user)

    def freshen(self):
        if self.download_url.startswith('svn'):
            svnUpdate(self.name)


class DownloadFile(object):
    """Mix-in that downloads an arbitrary file from the Internet

    The instance is required to have these attributes:

        self.name - the package name (e.g.  pyxml)
        self.download_url - the url from which to fetch the archive
        self.unarchived_name - the name of the top-level directory into which
                the archive will expand
    """

    def get(self):
        getArchive(self.download_url)

    # this isn't directly used by this mix-in, it's a helper for mix-ers
    @property
    def short_python_version(self):
        version = getVersion('python')
        # change a version number like 2.4.1 into one like 2.4
        return '.'.join(version.split('.')[:2])


class DistUtilsPackage(object):
    """Mix-in that unpacks and installs distutils packages
    
    The instance is required to have self.name set to the package name."""

    def build(self):
        # it doesn't make sence to "build" a distutils package
        pass

    def install(self):
        distutilsCommand(self.name, 'install')  

    def freshen(self):
        # it doesn't make sence to "freshen" a distutils package
        pass


class WindowsInstaller(object):
    """Mix-in that installs a binary Windows installer

    The instance is required to have these attributes:

        self.installer = the path to the installer
        self.install_marker - the path to a file such that if the file exists,
                the package has already been installed
    """

    def build(self):
        # nothing to do
        pass

    def install(self):
        if not os.path.exists(self.install_marker):
            installer = fileFromUrl(self.download_url)
            installer_path = os.path.join(getBaseArchivePath(), installer)
            runCommand(installer_path)

    def freshen(self):
        # nothing to do
        pass


class WindowsMsi(object):
    """Mix-in that installs an MSI

    The instance is required to have these attributes:

        self.installer = the path to the installer
        self.install_marker - the path to a file such that if the file exists,
                the package has already been installed
    """

    def build(self):
        # nothing to do
        pass

    def install(self):
        if not os.path.exists(self.install_marker):
            installer = fileFromUrl(self.download_url)
            msi_path = os.path.join(getBaseArchivePath(), installer)
            runCommand('msiexec', ['/i', msi_path], ignoreExitCode=True)

    def freshen(self):
        # nothing to do
        pass
