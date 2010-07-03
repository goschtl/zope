import unittest

class Test_optional_build_ext(unittest.TestCase):

    def _getTargetClass(self):
        from zope.optionalextension.build_ext import optional_build_ext
        return optional_build_ext

    def _makeOne(self, dist=None, stream=None):
        if dist is None:
            dist = self._makeDistribution()
        if stream is None:
            stream = self._makeStream()
        command = self._getTargetClass()(dist, stream)
        command.initialize_options()
        command.finalize_options()
        return command

    def _makeDistribution(self):
        from distutils.core import Distribution

        class DummyDistribution(Distribution):

            def has_c_libraries(self):
                return True

        return DummyDistribution()

    def _makeExtension(self, name, sources):
        from distutils.core import Extension

        class DummyExtension(Extension):
            pass

        return DummyExtension(name, sources)

    def _makeStream(self):
        from StringIO import StringIO
        return StringIO()

    def test_run(self):
        command = self._makeOne()
        command.extensions = [self._makeExtension('aaa', ['foo.c'])]
        command.run() # doesn't raise
        self.failUnless('CompileError' in command._stream.getvalue())

    def test_build_extension(self):
        command = self._makeOne()
        command.compiler = DummyCompiler()
        ext = self._makeExtension('aaa', ['foo.c'])
        command.build_extension(ext) # doesn't raise
        self.failUnless('TESTING' in command._stream.getvalue())


class DummyCompiler:
    def compile(self, *args, **kw):
        from distutils.errors import CCompilerError
        raise CCompilerError('TESTING')
