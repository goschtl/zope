from docutils import nodes
from sphinx.util.compat import Directive
from xmlrpclib import ServerProxy

import urllib
import socket
import threading


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
    if not app.config.buildbot_check:
        return
    socket_timeout = socket.getdefaulttimeout()
    try:
        socket.setdefaulttimeout(min(socket_timeout, 5))
        by_url = {}
        for node in doctree.traverse(BuildbotColor):
            url, builder = parse_builder_url(node.buildbot_url)
            by_url.setdefault(url, []).append((node, builder))
        jobs = []
        for url, nodes in by_url.items():
            thread = threading.Thread(target=update_buildbot_nodes,
                                      args=(url, nodes),
                                      name=url)
            thread.start()
            jobs.append(thread)
        for thread in jobs:
            thread.join()
    finally:
        socket.setdefaulttimeout(socket_timeout)


def parse_builder_url(url):
    """Parse a builder URL into buildbot URL and builder name."""
    url = url.rstrip('/') # make sure trailing slashes don't cause failures
    xmlrpc_url = '/'.join(url.split('/')[:-2] + ['xmlrpc'])
    builder = urllib.unquote(url.split('/')[-1])
    return xmlrpc_url, builder


def update_buildbot_nodes(url, nodes_and_builders):
    """Get build status of a number of builders and update document nodes.

    ``nodes_and_builders`` is a list of tuples (node, builder_name).
    """
    results = get_buildbot_results(url, [b for n, b in nodes_and_builders])
    for node, builder in nodes_and_builders:
        result = results[builder]
        if isinstance(result, Exception):
            node.css_class = 'tests_could_not_determine'
            node.title = '%s: %s' % (result.__class__.__name__, result)
        elif result:
            node.css_class = 'tests_passed'
        else:
            node.css_class = 'tests_not_passed'


def get_buildbot_results(xmlrpc_url, builders):
    """Return build status of a number of builders.

    ``builders`` is a list of builder names.

    Returns a dictionary mapping builder names to True/False or exception
    objects, in case of errors.
    """
    try:
        xmlrpc = ServerProxy(xmlrpc_url)
    except Exception, e:
        return dict.fromkeys(builders, e)
    results = {}
    for builder in builders:
        try:
            results[builder] = (xmlrpc.getLastBuildResults(builder) == 'success')
        except Exception, e:
            results[builder] = e
    return results


class BuildbotColor(nodes.Inline, nodes.TextElement):
    pass


def visit_buildbot_node(self, node):
    kwargs = {'href' : node.buildbot_url}
    css_class = getattr(node, 'css_class', '')
    if css_class:
        kwargs['class'] = css_class
    title = getattr(node, 'title', '')
    if title:
        kwargs['title'] = title
    self.body.append(self.starttag(node, 'a', **kwargs))
    self.body.append(node.text)


def depart_buildbot_node(self, node):
    self.body.append('</a>')

