import difflib
from OFS.History import historicalRevision
from DocumentTemplate.DT_Util import html_quote
from DateTime import DateTime

def getHistories(self):
    """Get a list of historic revisions. Returns metadata as well:

    (object, time, user)"""
    
    r = self._p_jar.db().history(self._p_oid, None, 20)

    if r is None:
        return ()

    # Build list of objects
    list = []
    for x in r:
        serial=x['serial']
        o = historicalRevision(self, serial)
        list.append((o.__of__(self.aq_parent), DateTime(x["time"]), x['description'], x['user_name']))

    return list

def getDocumentComparisons(self, max=10):
    histories = getHistories(self)

    html = ""

    if max > len(histories):
        max = len(histories)

    for rev in range(1,max):

        a, atime, adesc, auser = histories[rev]
        b, btime, bdesc, buser = histories[rev-1]
	if a.meta_type == 'ATDocument':
	    a = a.getText().split("\n")
	    b = b.getText().split("\n")
	else:
            a = a.text.split("\n")
            b = b.text.split("\n")

        html += """<h3>Vergleich: %s zu %s</h3>
          <dl><dt>Kommentar</dt><dd>%s</dd>
              <dt>Benutzer</dt><dd>%s</dd></dl>
              <div style="min-height:2em; border:1px solid grey; background-color:#eeeeee;">""" % \
                (self.toPortalTime(atime,1), self.toPortalTime(btime,1), adesc, auser
                        )

        lines = [x for x in difflib.unified_diff(a, b)][4:]

        new_lines = []
        for x in lines:
            x = html_quote(x)
            if x.startswith("+"):
                x = """<span style="color:green;">%s</span>""" % x
            elif x.startswith("-"):
                x = """<span style="color:red;">%s</span>""" % x
            elif x.startswith(" "):
                x = """&nbsp;%s""" % x
            elif x.startswith("@"):
                x = "<b>%s</b>" % x
            x = x+"<br/>"
            new_lines.append(x)


        html += "\n".join(new_lines)
        html += "</div>"
 
    return html 

