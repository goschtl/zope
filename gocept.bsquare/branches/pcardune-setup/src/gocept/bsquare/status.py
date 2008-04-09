# An extended web status display providing a cruise-control-like UI.

import urllib
import buildbot.status.web.base
import datetime
import os.path
import twisted.web.static


STATIC_DIR = os.path.join(os.path.dirname(__file__), 'static')


class OverviewStatusResource(buildbot.status.web.base.HtmlResource):

    title = "Buildbot Cruise-control"

    def _builder_status(self, builder):
        build = builder.getLastFinishedBuild()
        if build is None:
            stat = 'never'
        else:
            stat = build.getColor()
        return stat

    def head(self, request):
        return ('<link href="%s" rel="stylesheet" type="text/css" />' %
                request.sibLink('cruise.css'))

    def body(self, request):
        "This method builds the main waterfall display."

        data = ''

        status = self.getStatus(request)

        projectName = status.getProjectName()
        projectURL = status.getProjectURL()

        data += "<h1>%s</h1>" % projectName

        builders = [status.getBuilder(x) for x in
                status.getBuilderNames()]

        # Setup filters
        filters = []
        filter_status = request.args.get('status', [None])[0] or 'red'
        # Gah.
        if filter_status == 'None':
            filter_status = None
        # Double-gah!
        if filter_status != "any":
            filters.append(lambda x:self._builder_status(x) == filter_status)

        filter_prefix = request.args.get('prefix', [None])[0] or ''
        filters.append(lambda x:x.getName().startswith(filter_prefix))

        # Create totals
        status = {}
        for builder in builders:
            stat = self._builder_status(builder)
            if not stat in status:
                status[stat] = []
            status[stat].append(builder)

        data += '<form id="filter" action="%s">' % request.sibLink('cruise')
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
            data += '<div class="project %s %s"><h2>%s</h2>' % (
                self._builder_status(builder),
                activity, builder.getName())
            data += '<p><a href="%s">This builder is currently %s.</a></p>' % (
                request.childLink("../builders/" + urllib.quote(builder.name)),
                activity)
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



class ExtendedWebStatus(buildbot.status.web.baseweb.WebStatus):

    def __init__(self, *args, **kw):
        buildbot.status.web.baseweb.WebStatus.__init__(self, *args, **kw)

    def setupUsualPages(self):
        buildbot.status.web.baseweb.WebStatus.setupUsualPages(self)
        self.putChild('cruise', OverviewStatusResource())

        css = open(os.path.join(STATIC_DIR, 'cruise.css')).read()
        self.putChild('cruise.css', twisted.web.static.Data(css, 'text/css'))

        for image in ['headerbg.png', 'headerbg2.png', 'errorbg.png']:
            data = open(os.path.join(STATIC_DIR, image)).read()
            self.putChild(image, twisted.web.static.Data(data, 'image/png'))
