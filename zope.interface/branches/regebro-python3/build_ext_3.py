import os
import sys
from distutils.errors import (CCompilerError, DistutilsExecError, 
                              DistutilsPlatformError)
try:
    from setuptools.command.build_ext import build_ext
    from pkg_resources import (normalize_path, working_set, 
                               add_activation_listener, require)
except ImportError:
    from distutils.command.build_ext import build_ext
    

class optional_build_ext(build_ext):
    """This class subclasses build_ext and allows
       the building of C extensions to fail.
    """
    def run(self):
        try:
            build_ext.run(self)
        
        except DistutilsPlatformError as e:
            self._unavailable(e)

    def build_extension(self, ext):
        try:
            build_ext.build_extension(self, ext)
        
        except (CCompilerError, DistutilsExecError) as e:
            self._unavailable(e)

    def _unavailable(self, e):
        print('*' * 80, file=sys.stderr)
        print("""WARNING:

        An optional code optimization (C extension) could not be compiled.

        Optimizations for this package will not be available!""", file=sys.stderr)
        print(file=sys.stderr)
        print(e, file=sys.stderr)
        print('*' * 80, file=sys.stderr)
        
        
try:
    from distutils import log
    from lib2to3.refactor import RefactoringTool, get_fixers_from_package
    # These should be a part of the Python 3 setuptools port
    def run_2to3(files, fixer_names=None, options=None, explicit=None, doctests_only=False):
        """Invoke 2to3 on a list of Python files.
        The files should all come from the build area, as the
        modification is done in-place. To reduce the build time,
        only files modified since the last invocation of this
        function should be passed in the files argument."""
    
        if not files:
            return
    
        # Make this class local, to delay import of 2to3
        class DistutilsRefactoringTool(RefactoringTool):
            def log_error(self, msg, *args, **kw):
                log.error(msg, *args)
    
            def log_message(self, msg, *args):
                log.info(msg, *args)
    
            def log_debug(self, msg, *args):
                log.debug(msg, *args)
    
        if fixer_names is None:
            fixer_names = get_fixers_from_package('lib2to3.fixes')
        r = DistutilsRefactoringTool(fixer_names, options=options, explicit=explicit)
        r.refactor(files, write=True, doctests_only=doctests_only)
        
    class Mixin2to3:
        '''Mixin class for commands that run 2to3.
        To configure 2to3, setup scripts may either change
        the class variables, or inherit from individual commands
        to override how 2to3 is invoked.'''
    
        # provide list of fixers to run;
        # defaults to all from lib2to3.fixers
        fixer_names = None
    
        # options dictionary
        options = None
    
        # list of fixers to invoke even though they are marked as explicit
        explicit = None
    
        def run_2to3(self, files, doctests_only=False):
            return run_2to3(files, self.fixer_names, self.options, 
                            self.explicit, doctests_only=doctests_only)

    from setuptools.command.test import test
    class test_2to3(test):
        def with_project_on_sys_path(self, func):
            # Ensure metadata is up-to-date
            self.reinitialize_command('build_py', inplace=0)
            self.run_command('build_py')
            bpy_cmd = self.get_finalized_command("build_py")
            build_path = normalize_path(bpy_cmd.build_lib)
            
            self.reinitialize_command('egg_info', egg_base=build_path)
            self.run_command('egg_info')
            
            self.reinitialize_command('build_ext', inplace=0)
            self.run_command('build_ext')
    
            ei_cmd = self.get_finalized_command("egg_info")
    
            old_path = sys.path[:]
            old_modules = sys.modules.copy()
    
            try:
                sys.path.insert(0, build_path)
                working_set.__init__()
                add_activation_listener(lambda dist: dist.activate())
                require('%s==%s' % (ei_cmd.egg_name, ei_cmd.egg_version))
                func()
            finally:
                sys.path[:] = old_path
                sys.modules.clear()
                sys.modules.update(old_modules)
                working_set.__init__()
        
    from setuptools.command.build_py import build_py
    
    class build_py_2to3(build_py, Mixin2to3):
        def run(self):
            self.updated_files = []
            self.possible_doctests = []
    
            # Base class code
            if self.py_modules:
                self.build_modules()
            if self.packages:
                self.build_packages()
                self.build_package_data()
    
            # 2to3
            self.fixer_names = get_fixers_from_package('lib2to3.fixes') + \
                get_fixers_from_package('zope.fixers')
            self.run_2to3(self.updated_files)
            self.run_2to3(self.updated_files, doctests_only=True)
            self.run_2to3(self.possible_doctests, doctests_only=True)
    
            # Remaining base class code
            self.byte_compile(self.get_outputs(include_bytecode=0))
    
        def build_module(self, module, module_file, package):
            res = build_py.build_module(self, module, module_file, package)
            if res[1]:
                # file was copied
                self.updated_files.append(res[0])
            return res
        
        def build_package_data(self):
            """Copy data files into build directory"""
            lastdir = None
            for package, src_dir, build_dir, filenames in self.data_files:
                for filename in filenames:
                    target = os.path.join(build_dir, filename)
                    self.mkpath(os.path.dirname(target))
                    res = self.copy_file(os.path.join(src_dir, filename), target,
                                         preserve_mode=False)
                    if res[1]:
                        # file was copied
                        self.possible_doctests.append(res[0])
    
except ImportError:
    pass