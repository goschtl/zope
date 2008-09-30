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
"""Script to run Selenium tests.

$Id$
"""
from Queue import Queue, Empty
import optparse
import os
import random
import socket
import sys
import threading
import time
import urllib2
import webbrowser
import wsgiref.simple_server

from zope.testing import testrunner

from zc.selenium.pytest import selectTestsToRun

# Compute a default port; this is simple and doesn't ensure that the
# port is available, but does better than just hardcoding a port
# number.  The goal is to avoid browser cache effects due to resource
# changes (especially in JavaScript resources).
#
DEFAULT_PORT = "8034"

def run_zope(config, port):
    # This removes the script directory from sys.path, which we do
    # since there are no modules here.
    from zope.app.server.main import main
    main(["-C", config, "-X", "http0/address=" + port] + sys.argv[1:])

def make_wsgi_run_zope(app_path):
    module, name = app_path.rsplit('.', 1)
    app_factory = getattr(__import__(module, globals(), locals(), ["extra"]), name)
    def run_zope(config, port):
        server = wsgiref.simple_server.make_server(
            '0.0.0.0', int(port), app_factory(config))
        server.serve_forever()
    return run_zope

def run_tests(zope_thread, auto_start, browser_name, port, base_url):
    start_time = time.time()

    # wait for the server to start
    old_timeout = socket.getdefaulttimeout()
    socket.setdefaulttimeout(5)
    url = base_url % {'port': port}
    url += ('/@@/selenium/TestRunner.html'
            '?test=tests%%2FTestSuite.html&'
            'baseUrl=%s&'
            'resultsUrl=%s/@@/selenium_results' % (url,url,))
    time.sleep(1)
    while zope_thread.isAlive():
        try:
            urllib2.urlopen(url)
        except urllib2.URLError:
            time.sleep(1)
        else:
            break
    socket.setdefaulttimeout(old_timeout)

    if not zope_thread.isAlive():
        return

    # start the tests
    browser = webbrowser.get(browser_name)
    if auto_start:
        extra = '&auto=true'
    else:
        extra = ''
    browser.open(url + extra)

    # wait for the test results to come in (the reason we don't do a
    # blocking-get here is because it keeps Ctrl-C from working)
    exit_now = False
    while zope_thread.isAlive():
        try:
            time.sleep(0.1)
        except KeyboardInterrupt:
            exit_now = True

        try:
            results = messages.get(False)
        except Empty:
            if exit_now:
                break
        else:
            break

    time.sleep(1) # wait for the last request to finish so stdout is quiet

    if exit_now:
        return False

    print
    print 'Selenium test result:', results['result']
    if results['result'] != 'passed':
        print
        print results['log'].replace('\r', '')
        print
    print '%s tests passed, %s tests failed.' % (
              results['numTestPasses'], results['numTestFailures'])
    print ('%s commands passed, %s commands failed, %s commands had errors.'
           % (results['numCommandPasses'], results['numCommandFailures'],
              results['numCommandErrors']))
    print 'Elapsed time: %s seconds' % int(time.time() - start_time)
    print

    return results['result'] == 'passed'

def random_port():
    """Compute a random port number.

    This is simple and doesn't ensure that the port is available, but
    does better than just hardcoding a port number.  The goal is to
    avoid browser cache effects due to resource changes (especially in
    JavaScript resources).

    """
    port_offsets = range(1024)
    port_offsets.remove(0)
    port_offsets.remove(80) # ignore 8080 since that's often in use
    return str(random.choice(port_offsets) + 8000)

def parseOptions():
    if '--' in sys.argv:
        sep_index = sys.argv.index('--')
        extra_args = sys.argv[sep_index+1:]
        del sys.argv[sep_index:]
    else:
        extra_args = []

    # First arg is zope.conf file. This is provided by wrapper script
    config = sys.argv.pop(1)

    usage = 'usage: %prog [options] [-- runzope_options]'
    parser = optparse.OptionParser(usage)
    parser.add_option('-b', '--browser', metavar="BROWSER", default=None,
                      help='choose browser to use (mozilla, netscape, '
                      'kfm, internet-config)')
    parser.add_option('-k', '--keep-running',
                      action='store_true',
                      help='keep running after finishing the tests')
    parser.add_option('-A', '--no-auto-start', dest='auto_start',
                      action='store_false', default=True,
                      help='don\'t automatically start the tests (implies -k)')
    parser.add_option('-S', '--server-only', dest='server_only',
                      action='store_true',
                      help="Just start the Zope server. Don't run any tests")
    parser.add_option('-p', '--port', dest='port', default=DEFAULT_PORT,
                      help='port to run server on')
    parser.add_option('-r', '--random-port', dest='random_port',
                      action='store_true',
                      help='use a random port for the server')
    parser.add_option('-u', '--base-url', dest='base_url',
                      default='http://localhost:%(port)s/',
                      help='The base URL of the Zope site (may contain skin).')
    parser.add_option('-t', '--test', action="append", dest='tests',
                      help='specify tests to run')
    parser.add_option(
        '--coverage', action="store", type='string', dest='coverage',
        help="""\
        Perform code-coverage analysis, saving trace data to the directory
        with the given name.  A code coverage summary is printed to standard
        out.
        """)
    parser.add_option(
        '--package', '--dir', '-s', action="append", dest='package',
        help="A package to be included in the coverage report.")
    parser.add_option(
        '--wsgi_app', '-w', action="store", dest='wsgi_app',
        help="The path to the WSGI application to use.")

    options, positional = parser.parse_args()
    options.config = config
    sys.argv[1:] = extra_args
    return options

def main():
    global messages
    messages = Queue()

    # Hack around fact that zc.selenium.results expects zope to be run
    # from __main__:
    if __name__ != '__main__':
        sys.modules['__main__'] = sys.modules[__name__]

    options = parseOptions()
    if options.random_port:
        options.port = random_port()

    selectTestsToRun(options.tests)

    runner = run_zope
    if options.wsgi_app:
        runner = make_wsgi_run_zope(options.wsgi_app)

    if options.server_only:
        runner(options.config, port=options.port)
        sys.exit(0)

    if options.coverage:
        options.package = ('keas',)
        options.prefix = (('/', 'keas'),)
        options.test_path = []
        tracer = testrunner.TestTrace(options, trace=False, count=True)
        tracer.start()

    zope_thread = threading.Thread(
        target=runner, args=(options.config, options.port))
    zope_thread.setDaemon(True)
    zope_thread.start()
    test_result = run_tests(
        zope_thread, options.auto_start, options.browser, options.port,
        options.base_url)

    if options.coverage:
        tracer.stop()
        coverdir = os.path.join(os.getcwd(), options.coverage)
        res = tracer.results()
        res.write_results(summary=True, coverdir=coverdir)

    if options.keep_running or not options.auto_start:
        while True:
            time.sleep(10000)
    else:
        # exit with 0 if all tests passed, 1 if any failed
        sys.exit(not test_result)

if __name__ == '__main__':
    main()
