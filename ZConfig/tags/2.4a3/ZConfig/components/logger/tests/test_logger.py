##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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

"""Tests for logging configuration via ZConfig."""

import cStringIO as StringIO
import logging
import os
import sys
import tempfile
import unittest

import ZConfig

from ZConfig.components.logger import datatypes
from ZConfig.components.logger import handlers
from ZConfig.components.logger import loghandler


class CustomFormatter(logging.Formatter):
    def formatException(self, ei):
        """Format and return the exception information as a string.

        This adds helpful advice to the end of the traceback.
        """
        import traceback
        sio = StringIO.StringIO()
        traceback.print_exception(ei[0], ei[1], ei[2], file=sio)
        return sio.getvalue() + "... Don't panic!"


class LoggingTestBase(unittest.TestCase):

    # XXX This tries to save and restore the state of logging around
    # the test.  Somewhat surgical; there may be a better way.

    def setUp(self):
        self._created = []
        self._old_logger = logging.getLogger()
        self._old_level = self._old_logger.level
        self._old_handlers = self._old_logger.handlers[:]
        self._old_logger.handlers[:] = []
        self._old_logger.setLevel(logging.WARN)

        self._old_logger_dict = logging.root.manager.loggerDict.copy()
        logging.root.manager.loggerDict.clear()

    def tearDown(self):
        logging.root.manager.loggerDict.clear()
        logging.root.manager.loggerDict.update(self._old_logger_dict)

        for h in self._old_logger.handlers:
            self._old_logger.removeHandler(h)
        for h in self._old_handlers:
            self._old_logger.addHandler(h)
        self._old_logger.setLevel(self._old_level)

        while self._created:
            os.unlink(self._created.pop())

    def mktemp(self):
        fd, fn = tempfile.mkstemp()
        os.close(fd)
        self._created.append(fn)
        return fn

    def move(self, fn):
        nfn = self.mktemp()
        os.rename(fn, nfn)
        return nfn

    _schema = None

    def get_schema(self):
        if self._schema is None:
            sio = StringIO.StringIO(self._schematext)
            self.__class__._schema = ZConfig.loadSchemaFile(sio)
        return self._schema

    def get_config(self, text):
        conf, handler = ZConfig.loadConfigFile(self.get_schema(),
                                               StringIO.StringIO(text))
        self.assert_(not handler)
        return conf


class TestConfig(LoggingTestBase):

    _schematext = """
      <schema>
        <import package='ZConfig.components.logger'/>
        <section type='eventlog' name='*' attribute='eventlog'/>
      </schema>
    """

    def test_logging_level(self):
        # Make sure the expected names are supported; it's not clear
        # how to check the values in a meaningful way.
        # Just make sure they're case-insensitive.
        convert = datatypes.logging_level
        for name in ["notset", "all", "trace", "debug", "blather",
                     "info", "warn", "warning", "error", "fatal",
                     "critical"]:
            self.assertEqual(convert(name), convert(name.upper()))
        self.assertRaises(ValueError, convert, "hopefully-not-a-valid-value")

    def test_http_method(self):
        convert = handlers.get_or_post
        self.assertEqual(convert("get"), "GET")
        self.assertEqual(convert("GET"), "GET")
        self.assertEqual(convert("post"), "POST")
        self.assertEqual(convert("POST"), "POST")
        self.assertRaises(ValueError, convert, "")
        self.assertRaises(ValueError, convert, "foo")

    def test_syslog_facility(self):
        convert = handlers.syslog_facility
        for name in ["auth", "authpriv", "cron", "daemon", "kern",
                     "lpr", "mail", "news", "security", "syslog",
                     "user", "uucp", "local0", "local1", "local2",
                     "local3", "local4", "local5", "local6", "local7"]:
            self.assertEqual(convert(name), name)
            self.assertEqual(convert(name.upper()), name)
        self.assertRaises(ValueError, convert, "hopefully-never-a-valid-value")

    def test_config_without_logger(self):
        conf = self.get_config("")
        self.assert_(conf.eventlog is None)

    def test_config_without_handlers(self):
        logger = self.check_simple_logger("<eventlog/>")
        # Make sure there's a NullHandler, since a warning gets
        # printed if there are no handlers:
        self.assertEqual(len(logger.handlers), 1)
        self.assert_(isinstance(logger.handlers[0],
                                loghandler.NullHandler))

    def test_with_logfile(self):
        import os
        fn = self.mktemp()
        logger = self.check_simple_logger("<eventlog>\n"
                                          "  <logfile>\n"
                                          "    path %s\n"
                                          "    level debug\n"
                                          "  </logfile>\n"
                                          "</eventlog>" % fn)
        logfile = logger.handlers[0]
        self.assertEqual(logfile.level, logging.DEBUG)
        self.assert_(isinstance(logfile, loghandler.FileHandler))

    def test_with_stderr(self):
        self.check_standard_stream("stderr")

    def test_with_stdout(self):
        self.check_standard_stream("stdout")

    def check_standard_stream(self, name):
        old_stream = getattr(sys, name)
        conf = self.get_config("""
            <eventlog>
              <logfile>
                level info
                path %s
              </logfile>
            </eventlog>
            """ % name.upper())
        self.assert_(conf.eventlog is not None)
        # The factory has already been created; make sure it picks up
        # the stderr we set here when we create the logger and
        # handlers:
        sio = StringIO.StringIO()
        setattr(sys, name, sio)
        try:
            logger = conf.eventlog()
        finally:
            setattr(sys, name, old_stream)
        logger.warn("woohoo!")
        self.assert_(sio.getvalue().find("woohoo!") >= 0)

    def test_custom_formatter(self):
        old_stream = sys.stdout
        conf = self.get_config("""
        <eventlog>
        <logfile>
        formatter ZConfig.components.logger.tests.test_logger.CustomFormatter
        level info
        path STDOUT
        </logfile>
        </eventlog>
        """)
        sio = StringIO.StringIO()
        sys.stdout = sio
        try:
            logger = conf.eventlog()
        finally:
            sys.stdout = old_stream
        try:
            raise KeyError
        except KeyError:
            logger.exception("testing a KeyError")
        self.assert_(sio.getvalue().find("KeyError") >= 0)
        self.assert_(sio.getvalue().find("Don't panic") >= 0)

    def test_with_syslog(self):
        logger = self.check_simple_logger("<eventlog>\n"
                                          "  <syslog>\n"
                                          "    level error\n"
                                          "    facility local3\n"
                                          "  </syslog>\n"
                                          "</eventlog>")
        syslog = logger.handlers[0]
        self.assertEqual(syslog.level, logging.ERROR)
        self.assert_(isinstance(syslog, loghandler.SysLogHandler))

    def test_with_http_logger_localhost(self):
        logger = self.check_simple_logger("<eventlog>\n"
                                          "  <http-logger>\n"
                                          "    level error\n"
                                          "    method post\n"
                                          "  </http-logger>\n"
                                          "</eventlog>")
        handler = logger.handlers[0]
        self.assertEqual(handler.host, "localhost")
        # XXX The "url" attribute of the handler is misnamed; it
        # really means just the selector portion of the URL.
        self.assertEqual(handler.url, "/")
        self.assertEqual(handler.level, logging.ERROR)
        self.assertEqual(handler.method, "POST")
        self.assert_(isinstance(handler, loghandler.HTTPHandler))

    def test_with_http_logger_remote_host(self):
        logger = self.check_simple_logger("<eventlog>\n"
                                          "  <http-logger>\n"
                                          "    method get\n"
                                          "    url http://example.com/log/\n"
                                          "  </http-logger>\n"
                                          "</eventlog>")
        handler = logger.handlers[0]
        self.assertEqual(handler.host, "example.com")
        # XXX The "url" attribute of the handler is misnamed; it
        # really means just the selector portion of the URL.
        self.assertEqual(handler.url, "/log/")
        self.assertEqual(handler.level, logging.NOTSET)
        self.assertEqual(handler.method, "GET")
        self.assert_(isinstance(handler, loghandler.HTTPHandler))

    def test_with_email_notifier(self):
        logger = self.check_simple_logger("<eventlog>\n"
                                          "  <email-notifier>\n"
                                          "    to sysadmin@example.com\n"
                                          "    to sa-pager@example.com\n"
                                          "    from zlog-user@example.com\n"
                                          "    level fatal\n"
                                          "  </email-notifier>\n"
                                          "</eventlog>")
        handler = logger.handlers[0]
        self.assertEqual(handler.toaddrs, ["sysadmin@example.com",
                                           "sa-pager@example.com"])
        self.assertEqual(handler.fromaddr, "zlog-user@example.com")
        self.assertEqual(handler.level, logging.FATAL)

    def check_simple_logger(self, text, level=logging.INFO):
        conf = self.get_config(text)
        self.assert_(conf.eventlog is not None)
        self.assertEqual(conf.eventlog.level, level)
        logger = conf.eventlog()
        self.assert_(isinstance(logger, logging.Logger))
        self.assertEqual(len(logger.handlers), 1)
        return logger


class TestReopeningLogfiles(LoggingTestBase):

    # These tests should not be run on Windows.

    _schematext = """
      <schema>
        <import package='ZConfig.components.logger'/>
        <multisection type='logger' name='*' attribute='loggers'/>
      </schema>
    """

    _sampleconfig_template = """
      <logger>
        name  foo.bar
        <logfile>
          path  %s
          level debug
        </logfile>
        <logfile>
          path  %s
          level info
        </logfile>
      </logger>

      <logger>
        name  bar.foo
        <logfile>
          path  %s
          level info
        </logfile>
      </logger>
    """

    def test_filehandler_reopen(self):

        def mkrecord(msg):
            return logging.LogRecord(
                "foo.bar", logging.ERROR, __file__, 42, msg, (), ())

        fn = self.mktemp()
        h = loghandler.FileHandler(fn)
        h.handle(mkrecord("message 1"))
        nfn = self.move(fn)
        h.handle(mkrecord("message 2"))
        h.reopen()
        h.handle(mkrecord("message 3"))
        h.close()

        # Check that the messages are in the right files::
        text1 = open(nfn).read()
        text2 = open(fn).read()
        self.assert_("message 1" in text1)
        self.assert_("message 2" in text1)
        self.assert_("message 3" in text2)

    def test_logfile_reopening(self):
        paths = self.mktemp(), self.mktemp(), self.mktemp()
        text = self._sampleconfig_template % paths
        conf = self.get_config(text)
        assert len(conf.loggers) == 2
        # Build the loggers from the configuration, and write to them:
        conf.loggers[0]().info("message 1")
        conf.loggers[1]().info("message 2")
        npaths = [self.move(fn) for fn in paths]
        #
        # We expect this to re-open the original files, so we'll have
        # six files instead of three.
        #
        loghandler.reopenFiles()
        #
        # Write to them again:
        conf.loggers[0]().info("message 3")
        conf.loggers[1]().info("message 4")
        #
        # We should not have all six files:
        for fn in paths:
            self.assert_(os.path.isfile(fn), "%r must exist" % fn)
        for fn in npaths:
            self.assert_(os.path.isfile(fn), "%r must exist" % fn)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestConfig))
    if os.name != "nt":
        suite.addTest(unittest.makeSuite(TestReopeningLogfiles))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest="test_suite")
