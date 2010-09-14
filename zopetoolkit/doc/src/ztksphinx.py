from random import random
from docutils import nodes
from sphinx.util.compat import Directive, make_admonition
from xmlrpclib import ServerProxy

import urllib
import socket

def setup(app):
    app.add_config_value('buildbot_check', True, 'html')
    app.add_node(BuildbotColor,
                 html=(visit_buildbot_node, depart_buildbot_node))
    app.connect('doctree-resolved', process_buildbot_nodes)
    app.add_directive('buildbotresult', BuildbotDirective)

class BuildbotDirective(Directive):

    has_content = True
    required_arguments = 1
    optional_arguments = 1
    final_argument_whitespace = True

    def run(self):
        buildbot_url = self.arguments[0]
        text = self.arguments[1]
        targetnode = BuildbotColor('', '')
        targetnode.text = text
        targetnode.buildbot_url = buildbot_url

        return [targetnode]

def process_buildbot_nodes(app, doctree, fromdocname):
    if app.config.buildbot_check:
        socket_timeout = socket.getdefaulttimeout()
        try:
            socket.setdefaulttimeout(min(socket_timeout, 5))
            for node in doctree.traverse(BuildbotColor):
                buildbot_url = node.buildbot_url
                buildbot_result = getBuildbotResult(buildbot_url)
                css_class = buildbot_result and 'tests_passed' or \
                    'tests_not_passed'
                node.css_class = css_class
        finally:
            socket.setdefaulttimeout(socket_timeout)

def getBuildbotResult(url):
    try:
        xmlrpc_url = '/'.join(url.split('/')[:-2] + ['xmlrpc'])
        builder = urllib.unquote(url.split('/')[-1])
        xmlrpc = ServerProxy(xmlrpc_url)
        return xmlrpc.getLastBuildResults(builder) == 'success'
    except:
        return False

class BuildbotColor(nodes.Inline, nodes.TextElement):
    pass

def visit_buildbot_node(self, node):
    kwargs = {'href' : node.buildbot_url}
    css_class = getattr(node, 'css_class', '')
    if css_class:
        kwargs['CLASS'] = css_class
    self.body.append(self.starttag(node, 'a', **kwargs))
    self.body.append(node.text)

def depart_buildbot_node(self, node):
    self.body.append('</a>')

