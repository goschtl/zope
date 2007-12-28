##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
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
"""Grok test helpers
"""
from zope.configuration.config import ConfigurationMachine
from martian import scan
from grok import zcml

from os import listdir
import os.path
import re

class BasicTestSetup(object):

    extensions = ['.rst', '.txt']

    def __init__(self, package, filter_func=None, extensions=None, **kw):
        self.package = package
        self.filter_func = filter_func or self.isTestFile
        self.extensions = extensions or self.extensions
        self.additional_options = kw
        return

    def setUp(self, test):
        pass

    def tearDown(self, test):
        pass

    def fileContains(self, filename, regexp_list):
        """Does a file contain lines matching every of the regular
        expressions?
        """
        found_list = []
        try:
            for line in open(filename):
                for regexp in regexp_list:
                    if re.compile(regexp).match(line) and (
                        regexp not in found_list):
                        found_list.append(regexp)
                if len(regexp_list) == len(found_list):
                    break
        except IOError:
            # be gentle
            pass
        return len(regexp_list) == len(found_list)

    def isTestFile(self, filepath):
        """Return ``True`` if a file matches our expectations for a
        doctest file.
        """
        if os.path.splitext(filepath)[1].lower() not in self.extensions:
            return False
        return True

    def isTestDirectory(self, dirpath):
        """Check whether a given directory should be searched for tests.
        """
        if os.path.basename(dirpath).startswith('.'):
            # We don't search hidden directories like '.svn'
            return False
        return True

    def getDocTestFiles(self, dirpath=None, **kw):
        """Find all doctest files filtered by filter_func.
        """
        if dirpath is None:
            dirpath = os.path.dirname(self.package.__file__)
        dirlist = []
        for filename in listdir(dirpath):
            abs_path = os.path.join(dirpath, filename)
            if not os.path.isdir(abs_path):
                if self.filter_func(abs_path):
                    dirlist.append(abs_path)
                continue
            # Search subdirectories...
            if not self.isTestDirectory(abs_path):
                continue
            subdir_files = self.getDocTestFiles(dirpath=abs_path, **kw)
            dirlist.extend(subdir_files)
        return dirlist


def grok(module_name):
    config = ConfigurationMachine()
    zcml.do_grok('grok.meta', config)
    zcml.do_grok('grok.templatereg', config)
    zcml.do_grok(module_name, config)
    config.execute_actions()

def grok_component(name, component,
                   context=None, module_info=None, templates=None):
    if module_info is None:
        obj_module = getattr(component, '__grok_module__', None)
        if obj_module is None:
            obj_module = getattr(component, '__module__', None)
        module_info = scan.module_info_from_dotted_name(obj_module)

    module = module_info.getModule()
    if context is not None:
        module.__grok_context__ = context
    if templates is not None:
        module.__grok_templates__ = templates
    config = ConfigurationMachine()
    result = zcml.the_multi_grokker.grok(name, component,
                                         module_info=module_info,
                                         config=config)
    config.execute_actions()    
    return result
