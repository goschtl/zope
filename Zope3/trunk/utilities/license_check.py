#!/usr/bin/env python
##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
# 
##############################################################################
"""

$Id: license_check.py,v 1.2 2002/06/10 23:29:48 jim Exp $ 
"""

# small script to check all Python files for a correct header,
# specifically a presence of the correct license text from
# $ZOPE_HOME/zpl.py

usage = """\
%s looks for the presence of the right license text in
all Python files. It can be run in different modes.

usage: %s -c|-w|--undo [-s, -v, --nobackup] path 

-c : put a license text at the top of each file
-w : print the names of files without a license text
-s : strict checking. If this option is not set, only handle files
     without any form of license text. If set, an exact license text
     needs to be present
-v : be verbose
-h : Print this help

-l=path : Give the absolute path to zpl.py

--nobackup : Do not generate backup files
--include_init : Process also the __init__.py files
--undo : Rename the backup files to the original files, mainly for
         testing.

path : If not given start in the current directory. 

Example: To put a license in all files
license_check.py -c -v -s --nobackup --include_init 
"""


import os, fnmatch, sys
import re

class ZLicenseCheckError(Exception):
    fname = ''
    msg = ''
    def __init__(self, msg, fname):
        self.msg = msg
        self.fname = fname
        Exception.__init__(self, msg, fname)

    def __str__(self):
        return self.msg
 
class GlobDirectoryWalker:
    # a forward iterator that traverses a directory tree
    # snippet posted by Frederik Lundh in c.l.p.
    #
    def __init__(self, directory, pattern="*"):
        self.stack = [directory]
        self.pattern = pattern
        self.files = []
        self.index = 0


    def __getitem__(self, index):
        while 1:
            try:
                file = self.files[self.index]
                self.index = self.index + 1
            except IndexError:
                # pop next directory from stack
                self.directory = self.stack.pop()
                self.files = os.listdir(self.directory)
                self.index = 0
            else:
                # got a filename
                fullname = os.path.join(self.directory, file)
                if os.path.isdir(fullname) and not os.path.islink(fullname):
                    self.stack.append(fullname)
                if fnmatch.fnmatch(file, self.pattern):
                    return fullname

class HeaderCheck:
    """Make the header of a given file have a license text."""

    def __init__(self, fname, zpl, verbose=0, backup=1):
        """\
        fname -> name of the checked file
        zpl   -> instance of ZPL, class representing the license
        """
        self.fname = fname
        self.header_length = 700
        self.license = zpl.license_text
        self.verbose = verbose
        self.backup = backup
    

    def get_header(self):
        """Get a number if lines of the file. The number is an
        instance attribute"""
        header = open(self.fname,'r').read(self.header_length)
        return header
        

    def has_some_license(self):
        """Search the file for some license text. If the text is
        found, return 1"""
        header = self.get_header()
        if not re.search("ZPL", header, re.I):
            return 0
        else:
            return 1


    def has_license(self):
        """Fast check for the exact license text in the header"""
        header = self.get_header()
        if header.find(self.license) == -1:
            return 0
        else:
            return 1
            

    def include(self):
        """Put a license text at the top of the lines. If the first line
        starts with a bang-path start inserting at the second line"""
        lines = open(self.fname,'r').readlines()
        start = 0
        if lines and re.match('#!', lines[0]):
            start=1
        lines.insert(start, self.license)
        # keep the current stat_mod
        fmode = os.stat(self.fname)[0]
        # There can already be a backup file from the removal pass
        if self.backup and not os.path.isfile(self.fname+'.no_license'):
            os.rename(self.fname, self.fname+'.no_license')
        open(self.fname, 'w').write(''.join(lines))
        os.chmod(self.fname, fmode)
        if self.verbose:
            print 'License included: %s' % self.fname
        return 
 

    def change(self):
        """Try to change the license text in the file, raise an exception
        if not possible. 
        """
        if self.has_some_license():
            # try to remove the old license
            try:
                self.remove()
                self.include()
            except ZLicenseCheckError:
                open(self.fname+'.pathological','w')
                raise ZLicenseCheckError('License could not be changed',
                                         self.fname)

        else:
            self.include()
        return


    def remove(self):
        lines = open(self.fname, 'r').readlines()
        if not lines:
            return
        start = 0
        save = []
        if re.match('#!',lines[0]):
            start = 1
            save.extend(lines[0])
        end=start
        for line in lines[start:]:
            if line[0] == '#' or line.isspace():
                end += 1
            else:
                break

        license = ''.join(lines[start:end])
        # test if we really have the license
        lookfor = 'copyright|Zope Public|license|All rights reserved'
        if not re.search(lookfor, license, re.I):
            raise ZLicenseCheckError('No clear license text', self.fname)
        else:
            save.extend(lines[end:])
            # keep the current stat_mod
            fmode = os.stat(self.fname)[0]
            if self.backup:
                os.rename(self.fname, self.fname+'.no_license')
            if self.verbose:
                print 'License removed: %s' % self.fname
            open(self.fname,'w').write(''.join(save))
            os.chmod(self.fname, fmode)
        return
        

    def warn(self):
        print 'File %s has no license text' % self.fname

class Config:
    """Container to keep configuration options"""
    def __init__(self, **kws):
        self.verbose = 0
        self.warning = 0
        self.strict = 0
        self.backup = 1
        self.undo = 0
        self.include_init = 0
        self.license_path='./'

        if kws:
            for key,value in kws:
                setattr(self, key, value)

        return


class ZPL:    
    def __init__(self, path='./'):
        self.path = path
        self.license_text = self.get_text()

    def get_text(self):
        zhome = os.environ.get('ZOPE_HOME', self.path)
        try:
            data = open(os.path.join(zhome,'zpl.py'),'r').read()
        except IOError:
            sys.exit('Could not open license file zpl.py')

        license = data[:data.find('"""')]
        return license


class CheckerApp:
    def __init__(self, config):
        self.conf = config
        self.zpl = ZPL()
        self.pathological = []
        
        # Which test (uses unbound methods)
        if self.conf.strict:
            self.condition = HeaderCheck.has_license
        else:
            self.condition = HeaderCheck.has_some_license

        # Wich action
        if self.conf.warning:
            self.action = HeaderCheck.warn
        else:
            if self.conf.strict:
                self.action = HeaderCheck.change
            else:
                self.action = HeaderCheck.include
            
    def run(self):
        if self.conf.undo:
            for fname in GlobDirectoryWalker(self.conf.path,"*.no_license"):
                old_name = os.path.splitext(fname)[0]
                os.rename(fname, old_name)
        else:
            for fname in GlobDirectoryWalker(".", "*.py"):
                if (os.path.split(fname)[-1] == '__init__.py') and \
                        not self.conf.include_init:
                    if self.conf.verbose:
                        print 'Skipping: %s' % fname
                    continue

                hc = HeaderCheck(fname, self.zpl, 
                                 verbose=self.conf.verbose,
                                 backup=self.conf.backup)

                # unbound methods need an instance
                if not self.condition(hc):
                    try:
                        self.action(hc)
                    except ZLicenseCheckError, error:
                        print error, '(%s)' %error.fname
                        self.pathological.append(fname)

        if self.conf.verbose:
            for fname in self.pathological:
                print 'Could not be changed: %s' % fname
            print 'Number of pathological files: %s' % \
                   len(self.pathological) 


def print_usage(msg=0):
    print usage % (sys.argv[0], sys.argv[0])
    if msg:
        print msg
        msg=1
    sys.exit(msg)

    
def main():
    import getopt
    try:
        opts, args = getopt.getopt(sys.argv[1:], "vwcshl:",
        ["nobackup","undo","include_init"])
    except getopt.GetoptError, error:
        print_usage(str(error).capitalize())

    if not opts:
        print_usage('Need at least optin -w OR -c OR --undo')

    if (('-w','') in opts) and (('-c','') in opts):
        print_usage('Only option -w OR -c can be used')
        
    conf=Config()
    for o,a in opts:
        if o == '-v' : conf.verbose = 1
        elif o == '-c': conf.change = 1
        elif o == '-w': conf.warning = 1
        elif o == '-s': conf.strict = 1
        elif o == '-h': print_usage()
        elif o == '--include_init': conf.include_init = 1
        elif o == '--nobackup': conf.backup = 0
        elif o == '--undo': conf.undo = 1
        elif o == '-l':
            if not a:
                print_usage('Need to get a path for option -l')
            conf.license_path = a

    if not args:
        conf.path = os.getcwd()
    else:
        conf.path = args[0]

    # test presence of working directory
    if not os.path.isdir(conf.path):
        print_usage('Can not find directory %s' % conf.path)
        
    checker = CheckerApp(conf)
    checker.run()
    
    
if __name__ == '__main__':   
    main()
