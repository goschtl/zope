
import bobo

@bobo.query('/')
def index(bobo_request):
    conn = bobo_request.environ['zodb.connection']
    return "%r\n%r" % (
        conn.root(),
        conn.get_connection('index').root(),
        )
