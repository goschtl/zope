##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Helper to locate all the imports from a single source file.

$Id$
"""
import sys
import token
import tokenize

from zope.dependencytool.dependency import Dependency


START = "<start>"
FROM = "<from>"
FROM_IMPORT = "<from-import>"
IMPORT = "<import>"
COLLECTING = "<collecting>"
SWALLOWING = "<swallowing>"  # used to swallow "as foo"

TOK_COMMA = (token.OP, ",")
TOK_IMPORT = (token.NAME, "import")
TOK_FROM = (token.NAME, "from")
TOK_NEWLINE = (token.NEWLINE, "\n")
TOK_ENDMARK = (token.ENDMARKER, "")

dotjoin = ".".join


class ImportFinder(object):

    def __init__(self, packages=False):
        """Initialize the import finder.

        `packages` -- if true, reports package names rather than
          module names
        """
        self.packages = packages
        self.module_checks = {}
        self.deps = []
        self.imported_names = {}

    def get_imports(self):
        return self.deps

    def find_imports(self, f, path, package=None):
        """Find all the imported names in a source file.

        `f` -- open file
        `path` -- path of the source file
        `package` -- Python package the source file is contained in, or None
        """
        self.path = path
        self.package = package
        self.state = START
        self.post_name_state = None
        prevline = None
        try:
            for t in tokenize.generate_tokens(f.readline):
                type, string, start, end, line = t
                self.transition(type, string, start[0])
        except:
            print >>sys.stderr, "error finding imports in", path
            raise

    def add_import(self, name, lineno):
        """Record an import for `name`.

        `name` -- full dotted name as found in an import statement
          (may still be relative)

        `lineno` -- line number the import was found on
        """
        # is this a relative import?
        if self.package:
            fullname = "%s.%s" % (self.package, name)
            self.check_module_name(fullname)
            if not self.module_checks[fullname]:
                fullname = fullname[:fullname.rfind(".")]
                self.check_module_name(fullname)
            if self.module_checks[fullname]:
                # this was a relative import; use the full name:
                name = fullname
        if name not in self.module_checks:
            self.check_module_name(name)
            if not self.module_checks[name] and "." in name:
                # if "." isn't in name, I'd be very surprised!
                # i'd also be surprised if the result *isn't* a module
                name = dotjoin(name.split(".")[:-1])
                self.check_module_name(name)
        # A few oddball cases import __main__ (support for
        # command-line scripts), so we need to filter that out.
        if self.module_checks[name] and name != "__main__":
            if self.packages:
                name = package_for_module(name)
                if name is None:
                    # just drop it on the floor, since we're not
                    # interested in bare modules
                    return
            self.deps.append(Dependency(name, self.path, lineno))

    def check_module_name(self, name):
        """Check whether 'name' is a module name.  Update module_checks."""
        try:
            __import__(name)
        except ImportError:
            self.module_checks[name] = False
        else:
            self.module_checks[name] = name in sys.modules

    def transition(self, type, string, lineno):
        if type == tokenize.COMMENT:
            return
        entry = self.state_table.get((self.state, (type, string)))
        if entry is not None:
            self.state = entry[0]
            for action in entry[2:]:
                meth = getattr(self, "action_" + action)
                meth(type, string, lineno)
            if entry[1] is not None:
                self.post_name_state = entry[1]

        # gotta figure out what to do:
        elif self.state == COLLECTING:
            # watch for "as" used as syntax
            name = self.name
            if type == token.NAME and name and not name.endswith("."):
                self.state = SWALLOWING
                if self.prefix:
                    self.name = "%s.%s" % (self.prefix, name)
            else:
                self.name += string

        elif self.state in (START, SWALLOWING):
            pass

        else:
            raise RuntimeError(
                "invalid transition: %s %r" % (self.state, (type, string)))

    state_table = {
        # (state,     token):       (new_state,  saved_state, action...),
        (START,       TOK_IMPORT):  (COLLECTING, IMPORT, "reset"),
        (START,       TOK_FROM):    (COLLECTING, FROM,   "reset"),

        (FROM,        TOK_IMPORT):  (COLLECTING, FROM_IMPORT, "setprefix"),
        (FROM_IMPORT, TOK_COMMA):   (COLLECTING, FROM_IMPORT),
        (IMPORT,      TOK_COMMA):   (COLLECTING, IMPORT),

        (COLLECTING,  TOK_COMMA):   (COLLECTING, None,   "save", "poststate"),
        (COLLECTING,  TOK_IMPORT):  (COLLECTING, FROM_IMPORT, "setprefix"),

        (SWALLOWING,  TOK_COMMA):   (None,       None,   "save", "poststate"),

        # Commented-out transitions are syntax errors, so shouldn't
        # ever be seen in working code.

        # end of line:
        #(START,       TOK_NEWLINE): (START,      None,   "save", "reset"),
        #(FROM,        TOK_NEWLINE): (START,      None,   "save", "reset"),
        (FROM_IMPORT, TOK_NEWLINE): (START,      None,   "save", "reset"),
        #(IMPORT,      TOK_NEWLINE): (START,      None,   "save", "reset"),
        (COLLECTING,  TOK_NEWLINE): (START,      None,   "save", "reset"),
        (SWALLOWING,  TOK_NEWLINE): (START,      None,   "save", "reset"),

        # end of input:
        #(START,       TOK_ENDMARK): (START,      None,   "save", "reset"),
        #(FROM,        TOK_ENDMARK): (START,      None,   "save", "reset"),
        (FROM_IMPORT, TOK_ENDMARK): (START,      None,   "save", "reset"),
        #(IMPORT,      TOK_ENDMARK): (START,      None,   "save", "reset"),
        (COLLECTING,  TOK_ENDMARK): (START,      None,   "save", "reset"),
        (SWALLOWING,  TOK_ENDMARK): (START,      None,   "save", "reset"),
        }

    def action_reset(self, type, string, lineno):
        self.name = ''
        self.prefix = None

    def action_save(self, type, string, lineno):
        if self.name:
            assert not self.name.endswith("."), repr(self.name)
            name = self.name
            if self.prefix:
                name = "%s.%s" % (self.prefix, name)
            self.add_import(name, lineno)
            self.name = ""

    def action_setprefix(self, type, string, lineno):
        assert self.name, repr(self.name)
        assert not self.name.endswith("."), repr(self.name)
        self.prefix = self.name
        self.name = ""

    def action_collect(self, type, string, lineno):
        self.name += string

    def action_poststate(self, type, string, lineno):
        self.state = self.post_name_state
        self.post_name_state = None
        self.transition(type, string, lineno)


def package_for_module(name):
    """Return the package name for the module named `name`."""
    __import__(name)
    module = sys.modules[name]
    if not hasattr(module, "__path__"):
        if "." in name:
            name = name[:name.rfind(".")]
        else:
            name = None
    return name


def module_for_importable(name):
    """Return the module name for the importable object `name`."""
    try:
        __import__(name)
    except ImportError:
        while "." in name:
            name = name[:name.rfind(".")]
            try:
                __import__(name)
            except ImportError:
                pass
            else:
                break
        else:
            return None
    return name
