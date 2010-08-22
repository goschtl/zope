##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""base classes
"""
__docformat__ = 'ReStructuredText'
import StringIO
import base64
import httplib
import logging
import optparse
import os
import pkg_resources
import shutil
import subprocess
import sys
import stat
import urllib2
import urlparse
import xmlrpclib

LOGGER = logging.Logger('build')
formatter = logging.Formatter('%(levelname)s - %(message)s')

is_win32 = sys.platform == 'win32'

BUILD_SECTION = 'build'

class Command(object):
    def __init__(self, cwd=None, captureOutput=True, exitOnError=True):
        self.cwd = cwd
        self.captureOutput = captureOutput
        self.exitOnError = exitOnError

    def do(self, cmd):
        LOGGER.debug('Command: ' + cmd)
        if self.captureOutput:
            stdout = stderr = subprocess.PIPE
        else:
            stdout = stderr = None
        p = subprocess.Popen(
            cmd, stdout=stdout, stderr=stderr,
            shell=True, cwd=self.cwd)
        stdout, stderr = p.communicate()
        if stdout is None:
            stdout = "See output above"
        if stderr is None:
            stderr = "See output above"
        if p.returncode != 0:
            LOGGER.error(u'An error occurred while running command: %s' %cmd)
            LOGGER.error('Error Output: \n%s' % stderr)
            if self.exitOnError:
                sys.exit(p.returncode)
            else:
                raise OSError(p.returncode)
        LOGGER.debug('Output: \n%s' % stdout)
        return stdout

class SVN(object):

    user = None
    passwd = None
    forceAuth = False
    #hook to enable testing
    commandKlass = Command

    #TODO: spaces in urls+folder names???

    def __init__(self, user=None, passwd=None,
                 forceAuth=False, exitOnError=True):
        self.user = user
        self.passwd = passwd
        self.forceAuth = forceAuth
        self.cmd = self.commandKlass(exitOnError=exitOnError)

    def _addAuth(self, command):
        auth = ''
        if self.user:
            auth = '--username %s --password %s' % (self.user, self.passwd)

            if self.forceAuth:
                auth += ' --no-auth-cache'

        command = command.replace('##__auth__##', auth)
        return command

    def info(self, url):
        command = 'svn info --non-interactive ##__auth__## --xml %s' % url
        command = self._addAuth(command)
        return self.cmd.do(command)

    def ls(self, url):
        command = 'svn ls --non-interactive ##__auth__## --xml %s' % url
        command = self._addAuth(command)
        return self.cmd.do(command)

    def cp(self, fromurl, tourl, comment):
        command = 'svn cp --non-interactive ##__auth__## -m "%s" %s %s' %(
            comment, fromurl, tourl)
        command = self._addAuth(command)
        self.cmd.do(command)

    def co(self, url, folder):
        command = 'svn co --non-interactive ##__auth__## %s %s' % (url, folder)
        command = self._addAuth(command)
        self.cmd.do(command)

    def ci(self, folder, comment):
        command = 'svn ci --non-interactive ##__auth__## -m "%s" %s' % (
            comment, folder)
        command = self._addAuth(command)
        self.cmd.do(command)

class PYPI(object):
    def __init__(self):
        self.proxy = xmlrpclib.ServerProxy('http://pypi.python.org/pypi')

    def list_packages(self):
        pass

    def package_releases(self, package_name, show_hidden=False):
        return self.proxy.package_releases(package_name, show_hidden)

    def release_urls(self, package_name, version):
        pass

    def release_data(self, package_name, version):
        pass

    def search(self, spec, operator=None):
        pass

    def changelog(self, since):
        pass

class URLGetter(object):
    def get(self, url):
        req = urllib2.Request(url)
        return urllib2.urlopen(req).read()

def getInput(prompt, default, useDefaults):
    if useDefaults:
        return default
    defaultStr = ''
    if default:
        defaultStr = ' [' + default + ']'
    value = raw_input(prompt + defaultStr + ': ')
    if not value:
        return default
    return value


def checkRO(function, path, excinfo):
    if (function == os.remove
        and excinfo[0] == WindowsError
        and excinfo[1].winerror == 5):
        #Access is denied
        #because it's a readonly file
        os.chmod(path, stat.S_IWRITE)
        os.remove(path)

def rmtree(dirname):
    if is_win32:
        shutil.rmtree(dirname, ignore_errors=False, onerror=checkRO)
    else:
        shutil.rmtree(dirname)

parser = optparse.OptionParser()
parser.add_option(
    "-q", "--quiet", action="store_true",
    dest="quiet", default=False,
    help="When specified, no messages are displayed.")

parser.add_option(
    "-v", "--verbose", action="store_true",
    dest="verbose", default=False,
    help="When specified, debug information is displayed.")

parser.add_option(
    "-d", "--dryrun", action="store_true",
    dest="dryrun", default=False,
    help="When specified, no upload is done.")

parser.add_option(
    "-s", "--status", action="store_true",
    dest="status", default=False,
    help="When specified, detailed status is output at the end.")
