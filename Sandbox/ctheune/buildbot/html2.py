# -*- test-case-name: buildbot.test.test_web -*-

from __future__ import generators

from twisted.python import log, components
import urllib, re
import datetime

from twisted.internet import defer, reactor
from twisted.web.resource import Resource
from twisted.web import static, html, server, distrib
from twisted.web.error import NoResource
from twisted.web.util import Redirect, DeferredResource
from twisted.application import strports
from twisted.spread import pb

from buildbot.twcompat import implements, Interface

import sys, string, types, time, os.path

from buildbot import interfaces, util
from buildbot import version
from buildbot.sourcestamp import SourceStamp
from buildbot.status import builder, base
from buildbot.changes import changes
from buildbot.process.base import BuildRequest

NO_FILTER = object()

class HtmlResource(Resource):
    css = None
    contentType = "text/html; charset=UTF-8"
    title = "Dummy"

    def render(self, request):
        data = self.content(request)
        if isinstance(data, unicode):
            data = data.encode("utf-8")
        request.setHeader("content-type", self.contentType)
        if request.method == "HEAD":
            request.setHeader("content-length", len(data))
            return ''
        return data

    def content(self, request):
        data = ('<!DOCTYPE html PUBLIC'
                ' "-//W3C//DTD XHTML 1.0 Transitional//EN"\n'
                '"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\n'
                '<html'
                ' xmlns="http://www.w3.org/1999/xhtml"'
                ' lang="en"'
                ' xml:lang="en">\n')
        data += "<head>\n"
        data += "  <title>" + self.title + "</title>\n"
        data += '  <link href="http://uter.gocept.com/~ctheune/buildbot/buildbot.css" media="all" rel="Stylesheet" type="text/css" />'
        if self.css:
            # TODO: use some sort of relative link up to the root page, so
            # this css can be used from child pages too
            data += ('  <link href="%s" rel="stylesheet" type="text/css"/>\n'
                     % "buildbot.css")
        data += "</head>\n"
        data += '<body>\n'
        data += self.body(request)
        data += "</body></html>\n"
        return data

    def body(self, request):
        return "Dummy\n"


class OverviewStatusResource(HtmlResource):
    """This builds the main status page, with the waterfall display, and
    all child pages."""
    title = "BuildBot"
    def __init__(self, status, changemaster):
        HtmlResource.__init__(self)
        self.status = status
        self.changemaster = changemaster
        p = self.status.getProjectName()
        if p:
            self.title = "BuildBot: %s" % p

    def _builder_status(self, builder):
        build = builder.getLastFinishedBuild()
        if build is None:
            stat = 'never'
        else:
            stat = build.getColor()
        return stat

    def body(self, request):
        "This method builds the main waterfall display."

        data = ''

        data += """<script lang="javascript">
        window.setTimeout("reload()", 10000);
        function reload() {
            document.forms['filter'].submit();
        };
        </script>
        """

        projectName = self.status.getProjectName()
        projectURL = self.status.getProjectURL()

        data += "<h1>%s &mdash; THIS IS STILL EXPERIMENTAL AND UNDER DEVELOPMENT!</h1>" % projectName

        builders = [self.status.getBuilder(x) for x in 
                self.status.getBuilderNames()]

        # Setup filters
        filters = []
        filter_status = request.args.get('status', [None])[0] or 'red'
        # Gah.
        if filter_status == 'None':
            filter_status = None
        # Double-gah!
        if filter_status != "any":
            filters.append(lambda x:self._builder_status(x) == filter_status)

        filter_prefix = request.args.get('prefix', [None])[0] or 'zope.'
        filters.append(lambda x:x.getName().startswith(filter_prefix))

        # Create totals
        status = {}
        for builder in builders:
            stat = self._builder_status(builder)
            if not stat in status:
                status[stat] = []
            status[stat].append(builder)

        data += '<form id="filter" action=".">'
        data += '<div id="status-blocks">'
        for stat, affected in status.items():
            if stat == filter_status:
                selected = 'checked="checked"'
            else:
                selected = ""
            data += '<div class="%s"><h3><label><input type="radio" name="status" value="%s" %s/> %s</label></h3><p>%s projects</p></div>' % (stat, stat, selected, stat, len(affected))

        if filter_status == "any":
            selected = 'checked="checked"'
        else:
            selected = ''
        data += '<div><h3><label><input type="radio" name="status" value="any" %s/> Any</label></h3><p>&nbsp;</p></div>' % selected

        data += "</div>"
        data += '<div class="clear"/>'
        data += '<div><label for="prefix">Show only projects starting with</label> <input type="text" name="prefix" value="%s"/> <input type="submit" value="Set filter"/></div>' % filter_prefix
        data += '</form>'

        # Apply filters on builders
        for f in filters:
            builders = filter(f, builders)
        data += "<p>Showing %i projects matching the current filter.</p>" % len(builders)

        # Create detail view panels
        for builder in builders:
            activity = builder.getState()[0]
            data += '<div class="project %s %s"><h2>%s</h2>' % (self._builder_status(builder),
                    activity, builder.getName())
            data += '<p>This builder is currently %s.</p>' % activity
            data += "<ul>"
            for x in range(1,6):
                build = builder.getBuild(-x)
                if build is None:
                    break
                reason = build.reason
                started = datetime.datetime.fromtimestamp(build.started)
                started = started.strftime('%d %b, %H:%M')
                if build.source.changes:
                    change = build.source.changes[0]
                    reason = "%s by %s: %s" % (change.revision, change.who, change.comments)
                data += '<li style="color:%s;">%s &ndash; %s</li>' % (
                        build.color, started, reason)
            data += "</ul>"
            data += "</div>"

        return data

class StatusResource(Resource):
    status = None

    def __init__(self, status, changemaster):
        Resource.__init__(self)
        self.status = status
        self.changemaster = changemaster
        overview = OverviewStatusResource(self.status, changemaster)
        self.putChild("", overview)

    def render(self, request):
        request.redirect(request.prePathURL() + '/')
        request.finish()


class CompactOverview(base.StatusReceiverMultiService):

    compare_attrs = ["http_port"]

    def __init__(self, http_port=None):
        base.StatusReceiverMultiService.__init__(self)
        if type(http_port) is int:
            http_port = "tcp:%d" % http_port
        self.http_port = http_port

    def __repr__(self):
        return "<CompactOverview on port %s>" % self.http_port

    def setServiceParent(self, parent):
        """
        @type  parent: L{buildbot.master.BuildMaster}
        """
        base.StatusReceiverMultiService.setServiceParent(self, parent)
        self.setup()

    def setup(self):
        status = self.parent.getStatus()
        change_svc = self.parent.change_svc
        sr = StatusResource(status, change_svc)
        self.site = server.Site(sr)
        s = strports.service(self.http_port, self.site)
        s.setServiceParent(self)
