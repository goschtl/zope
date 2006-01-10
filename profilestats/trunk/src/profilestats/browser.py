##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""Stats views

$Id$
"""
import marshal, urllib, cgi

from zope.app.pagetemplate import ViewPageTemplateFile
import zope.app.form.browser
from zope.formlib import form
from zope import schema, interface

import profilestats.stats


class Add(form.AddForm):

    form_fields = (
        form.Field(
            schema.Bytes(__name__='file',
                         title=u"profile stats file"),
            custom_widget = zope.app.form.browser.FileWidget,
            ),
        )

    def create(self, data):
        return profilestats.stats.Stats(marshal.loads(data['file']))
        
        
class StatsView:

    detail_template = ViewPageTemplateFile('detail.pt')
    table_template = ViewPageTemplateFile('table.pt')
    tree_template = ViewPageTemplateFile('tree.pt')

    def __init__(self, stats, request):
        self.context = stats
        self.stats = stats.stats
        self.request = request

    def tree(self):
        """Show profile results as a tree
        """

        class Tree(dict):

            def __init__(self, name='', time=0.0):
                self.name = name
                self.time = time

        tree = Tree()
        for ((filename, lineno, func),
             (direct_calls, calls, time, cummulative, callers)
             ) in self.stats.iteritems():
            if not calls:
                continue
            
            t = tree
            t.time += time
            for n in filename.split('/'):
                tn = t.get(n)
                if tn is None:
                    tn = t[n] = Tree(n)
                t = tn
                t.time += time

            name = func
            if lineno:
                name = "(%s) %s" % (lineno, name)

            url = 'detail.html?filename=%s&lineno=%s&func=%s' % (
                urllib.quote(filename, ""), lineno, urllib.quote(func))

            name = '<a href="%s">%s</a>' % (url, name)

            t[name] = Tree(name, time)


        def simplify_tree(tree):
            while len(tree) == 1:
                k = tree.keys()[0]
                v = tree.pop(k)
                tree.name += '/' + k
                tree.update(v)

            for t in tree.itervalues():
                simplify_tree(t)

        simplify_tree(tree)
            
        def showtree(tree, write, style=''):
            items = sorted(tree.iteritems())
            if items and style:
                write('<a onclick="toggle_visibility(this);">+</a>')
            write('%s <span class="time">%s</span>' % (tree.name, tree.time))
            if items:
                write("<div>")
                for name, subtree in items:
                    if subtree.time == 0.0:
                        continue
                    write("<div %s>" % style)
                    showtree(subtree, write,
                             'style="display:none;padding-left:2em"')
                    write("</div>")
                write("</div>")

        results = []
        showtree(tree, results.append)
                
        return self.tree_template(tree="\n".join(results))

        
    def _table_data(self):
        table = []
        total = 0
        for ((filename, lineno, func),
             (direct_calls, calls, time, cummulative, callers)
             ) in self.stats.iteritems():

            if calls < 1:
                continue

            table.append(dict(
                calls=scalls(calls, direct_calls),
                time=time,
                timeper=time*1e6/calls,
                cummulative=cummulative,
                cummulativeper=cummulative*1e6/direct_calls,
                link=link(filename, lineno, func),
                ))
            total += time

        return table, total

    def byTime(self):
        data, total = self._table_data()
        return self.table_template(
            sortby="time",
            total=total,
            data=sorted(data, key=lambda row: -row['time']),
            )

    def byCumulative(self):
        data, total = self._table_data()
        return self.table_template(
            sortby="cummulative",
            total=total,
            data=sorted(data, key=lambda row: -row['cummulative']),
            )

    def detail_data(self, filename, lineno, func):
        stats = self.stats
        key = (filename, int(lineno), func)
        direct_calls, calls, time, cummulative, callers = stats[key]

        callees = []
        for (callee, callee_data) in stats.iteritems():
            called = callee_data[-1].get(key)
            if called is not None:
                callees.append((callee, called))

        return dict(
            filename=filename,
            lineno=lineno,
            func=func,
            scalls=scalls(calls, direct_calls),
            time=time,
            timeper=time*1e6/calls,
            cummulative=cummulative,
            cummulativeper=cummulative*1e6/direct_calls,
            callers=[
                (link(*caller), n,
                 time*n/calls,
                 (caller != key) and (cummulative*n/direct_calls) or 0,
                 )
                for (caller, n) in sorted(callers.iteritems())
                ],
            callees=[
                (link(*callee), n,
                 n*time_per(stats, callee),
                 (callee != key) and (n*cummulative_per(stats, callee)) or 0,
                 )
                for (callee, n) in sorted(callees)
                ],
            )

    def detail(self, filename, lineno, func):
        return self.detail_template(**self.detail_data(filename, lineno, func))

def time_per(stats, key):
    direct_calls, calls, time, cummulative, callers = stats[key]
    return time/calls

def cummulative_per(stats, key):
    direct_calls, calls, time, cummulative, callers = stats[key]
    return time/direct_calls

def link(filename, lineno, func):
    url = 'detail.html?filename=%s&lineno=%s&func=%s' % (
        urllib.quote(filename, ""), lineno, urllib.quote(func))
    return '<a href="%s">%s(%s) %s</a>' % (
        url,
        cgi.escape(filename),
        lineno,
        cgi.escape(func),
        )

def scalls(calls, direct_calls):
    if calls == direct_calls:
        return str(calls)
    return "%s/%s" % (calls, direct_calls)
