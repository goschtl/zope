"""Obviously, this isn't really a CMS application.

It's just a placeholder so that we can tell a story about deployment.
"""
import bobo

@bobo.query('/')
def index(bobo_request):
    conn = bobo_request.environ['zodb.connection']
    return "%r\n%r" % (
        conn.root(),
        conn.get_connection('index').root(),
        )
