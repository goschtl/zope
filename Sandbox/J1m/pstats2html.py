#!/usr/local/bin/python2.4
##############################################################################
#
# Copyright (c) Zope Corporation and Contributors.
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
import cgi, marshal, math, urllib, string, sys

def template(s):
    return string.Template(s).substitute

head_template = template("""
<head>
  <title>profile statistics for $label</title>
  <script type="text/javascript" language="JavaScript1.3">
    function toggle_visibility(element) {
        element.normalize();
        var label = element.childNodes[0]
        if (label.data == '+') {
           label.data = '-';
        } else {
           label.data = '+';
        }

        var lower = element.nextSibling.nextSibling.nextSibling.nextSibling

        // if this is a leaf node, there is nothing to do
        if (lower == undefined) return;

        lower = lower.childNodes;
        for (var i=0; i < lower.length; i++) {
          child = lower[i];
          if (child.style != undefined) {
            if (child.style.display == 'none') {
                child.style.display = '';
            } else {
                child.style.display = 'none';
            }
          }
        }
      }
  </script>
</head>""")


tree_template = template(r"""
  <h2>Profile results for $label,
      organized by file and function</h2>
  Total time is $tree""")

table_template = template(r'''
  <a name="table-$sortby"></a>
  <h2>Profile results for $label, sorted by $sortby</h2>

  <p>Total time: $total</p>

  <table border=1>
    <tr>
      <th><a href="#table-calls">calls</a></th>
      <th><a href="#table-time">time</a></th>
      <th><a href="#table-timeper">time per call &mu;s</a></th>
      <th><a href="#table-cummulative">cummulative time</a></th>
      <th><a href="#table-cummulativeper">cummulative time per call &mu;s</a>
          </th>
      <th>function</th>
    </tr>
$rows
  </table>
''')

row_template = template("""
    <tr tal:repeat="row options/data">
      <td class="calls">$scalls</td>
      <td class="time">$time</td>
      <td class="timeper">$timeper</td>
      <td class="cummulative">$cummulative</td>
      <td class="cummunlativeper">$cummulativeper</td>
      <td class="link">$link</td>
    </tr>
""")

detail_template = template('''
  <a name="detail-$detail_id"></a>
  <h2>Details for <a href="file://$filename">$filename</a>($lineno) $func
      in profile results $label
  </h2>

  <table>
    <tr><td><a href="#table-calls">Calls</a>:</td>
        <td>$scalls</td></tr>
    <tr><td><a href="#table-time">Time</a>:</td>
        <td>$time</td></tr>
    <tr><td><a href="#table-timeper">Time per call &mu</a>;s:</td>
        <td>$timeper</td></tr>
    <tr><td><a href="#table-cummulative">Cummulative time</a>:</td>
        <td>$cummulative</td></tr>
    <tr><td><a href="#table-cummulativeper">Cummulative time per call &mu;s</a>:</td>
        <td>$cummulativeper</td></tr>
  </table>

$callers
$callees
''')

detail_call_template = template('''
    <h3>$kind</h3>
    <table border=1>
      <tr>
      <th>function</th>
      <th>calls</th>
      <th>time credited to function</th>
      <th>cummulative time credited to function</th>
      </tr>
$rows
    </table>
''')

class StatsView:

    def __init__(self, name, comment='', delimiter='/', label=None):
        self.name = name
        self.comment = comment
        self.delimiter = delimiter
        self.stats = marshal.load(open(name))
        self.label = label or name
        self.detail_ids = dict([(k, i)
                                for (i, k) in enumerate(sorted(self.stats))
                                ])

    def tree(self):
        """Show profile results as a tree
        """

        class Tree(dict):

            def __init__(self, name='', time=0.0):
                self.name = name
                self.time = time

        delimiter = self.delimiter
        tree = Tree()
        for ((filename, lineno, func),
             (direct_calls, calls, time, cummulative, callers)
             ) in self.stats.iteritems():
            if not calls:
                continue
            
            t = tree
            t.time += time
            for n in filename.split(delimiter):
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
                tree.name += delimiter + k
                tree.update(v)

            for t in tree.itervalues():
                simplify_tree(t)

        simplify_tree(tree)
            
        def showtree(tree, write, style=''):
            items = sorted(tree.iteritems())
            if items and style:
                write('<a onclick="toggle_visibility(this);">+</a>')
            write('%s <span class="time">%s</span>'
                  % (tree.name, format(tree.time))
                  )
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
                
        return tree_template(label=self.label, tree="\n".join(results))
        
    def _table_data(self):
        table = []
        total = 0
        for ((filename, lineno, func),
             (direct_calls, calls, time, cummulative, callers)
             ) in self.stats.iteritems():

            if calls < 1:
                continue

            table.append(dict(
                calls=calls,
                scalls=scalls(calls, direct_calls),
                time=time,
                timeper=time*1e6/calls,
                cummulative=cummulative,
                cummulativeper=cummulative*1e6/direct_calls,
                link=self.link(filename, lineno, func),
                ))
            total += time

        return table, total

    def table(self, sortby, reverse=True):
        if reverse:
            key = lambda row: -row[sortby]
        else:
            key = lambda row: row[sortby]
            
        data, total = self._table_data()
        return table_template(
            label=self.label,
            sortby=sortby,
            total=total,
            rows = "".join([row_template(dict([(name, format(v))
                                               for (name, v) in row.items()]
                                              ))
                            for row in sorted(data, key=key)
                            ]),
            )

    def detail_data(self, filename, lineno, func):
        stats = self.stats
        key = (filename, int(lineno), func)
        direct_calls, calls, time, cummulative, callers = stats[key]
        if not calls:
            return None

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
            time=format(time),
            timeper=format(time*1e6/calls),
            cummulative=format(cummulative),
            cummulativeper=format(cummulative*1e6/direct_calls),
            callers=[
                (self.link(*caller), n,
                 format(time*n/calls),
                 (caller != key) and format(cummulative*n/direct_calls) or 0,
                 )
                for (caller, n) in sorted(callers.iteritems())
                ],
            callees=[
                (self.link(*callee), n,
                 format(n*time_per(stats, callee)),
                 (callee != key)
                 and format(n*cummulative_per(stats, callee))
                 or 0,
                 )
                for (callee, n) in sorted(callees)
                ],
            )

    def detail_call_text(self, kind, data):
        if not data:
            return ''
        return detail_call_template(
            kind=kind,
            rows = "".join([("<tr><td>%s</td></tr>\n"
                             % ("</td><td>".join(map(str, row))))
                            for row in data
                            ]),
            )

    def detail(self, filename, lineno, func):
        data = self.detail_data(filename, lineno, func)
        if data is None:
            return ''
        return detail_template(
            data,
            detail_id=self.detail_ids[(filename, lineno, func)],
            label=self.label,
            callers=self.detail_call_text('callers', data['callers']),
            callees=self.detail_call_text('callees', data['callees']),
            )

    def render(self, write):
        write("<html>\n"+head_template(label=self.label)+'<body>\n')
        write(self.tree())
        write(self.table("time"))
        write(self.table("cummulative"))
        write(self.table("timeper"))
        write(self.table("cummulativeper"))
        write(self.table("calls"))
        for key in sorted(self.stats):
            write(self.detail(*key))
        write("</body></html>\n")


    def link(self, *key):
        filename, lineno, func = key
        id = self.detail_ids[key]
        url = '#detail-%s' % id
        return '<a href="%s">%s(%s) %s</a>' % (
            url,
            cgi.escape(filename),
            lineno,
            cgi.escape(func),
            )


def time_per(stats, key):
    direct_calls, calls, time, cummulative, callers = stats[key]
    return time/calls

def cummulative_per(stats, key):
    direct_calls, calls, time, cummulative, callers = stats[key]
    return time/direct_calls

def scalls(calls, direct_calls):
    if calls == direct_calls:
        return str(calls)
    return "%s/%s" % (calls, direct_calls)

def format(n):
    if not isinstance(n, float):
        return n

    if n==0:
        return n

    l = int(-math.log10(n)) + 2
    if l < 0:
        return str(int(round(n, l)))
    else:
        return "%%.%sf" % l % n
        

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    [stats] = argv

    view = StatsView(stats)
    view.render(open(stats+'.html', 'w').write)

if __name__ == '__main__':
    main()

