When ICP is Useful
==================

When generating content dynamically, having all the data available locally to
fulfil a request can have a profound effect on service time.  One approach to
having the data available is to have one or more caches.  In some situations
those caches are not large enough to contain the entire working set required
for efficient servicing of incoming requests.  Adding additional request
handlers (servers or processes) doesn't help because the time to load the data
from one or more storage servers (e.g., databases) is the dominant factor in
request time.  In those situations the request space can be partitioned such
that the portion of the working set a particular handler (server or process) is
responsible for can fit in its cache(s).

Statically configuring request space partitioning may be difficult,
error-prone, or even impossible.  In those circumstances it would be nice to
let the origin servers provide feedback on whether or not they should handle a
particular request.  That's where ICP comes in.


Hits and Misses
===============

When an ICP query request is received, the server can return one of ICP_OP_HIT,
ICP_OP_MISS, ICP_OP_ERR, ICP_OP_MISS_NOFETCH, or ICP_OP_DENIED.  The meanings
of these result codes are defined in the ICP RFC as below.

ICP_OP_HIT
    An ICP_OP_HIT response indicates that the requested URL exists in
    this cache and that the requester is allowed to retrieve it.

ICP_OP_MISS
    An ICP_OP_MISS response indicates that the requested URL does not
    exist in this cache.  The querying cache may still choose to fetch
    the URL from the replying cache.

ICP_OP_ERR
    An ICP_OP_ERR response indicates some kind of error in parsing or
    handling the query message (e.g. invalid URL).

ICP_OP_MISS_NOFETCH
    An ICP_OP_MISS_NOFETCH response indicates that this cache is up,
    but is in a state where it does not want to handle cache misses.
    An example of such a state is during a startup phase where a cache
    might be rebuilding its object store.  A cache in such a mode may
    wish to return ICP_OP_HIT for cache hits, but not ICP_OP_MISS for
    misses.  ICP_OP_MISS_NOFETCH essentially means "I am up and
    running, but please don't fetch this URL from me now."

    Note, ICP_OP_MISS_NOFETCH has a different meaning than
    ICP_OP_MISS.  The ICP_OP_MISS reply is an invitation to fetch the
    URL from the replying cache (if their relationship allows it), but
    ICP_OP_MISS_NOFETCH is a request to NOT fetch the URL from the
    replying cache.

ICP_OP_DENIED
    An ICP_OP_DENIED response indicates that the querying site is not
    allowed to retrieve the named object from this cache.  Caches and
    proxies may implement complex access controls.  This reply must be
    be interpreted to mean "you are not allowed to request this
    particular URL from me at this particular time."

Because we want to use ICP to communicate about whether or not an origin server
(as opposed to a cache server) wants to handle a particular request, we will
use slightly different definitions for some of the result codes.

ICP_OP_HIT
    An ICP_OP_HIT response indicates that the queried server would prefer to
    handle the HTTP request.  The reason the origin server is returning a hit
    might be that it has recently handled "similar" requests, or that it has
    been configured to handle the partition of the URL space occupied by the
    given URL.

ICP_OP_MISS
    An ICP_OP_MISS response indicates that the queried server does not have a
    preference to service the request, but will be able to handle the request
    nonetheless.  This is normally the default response.

ICP_OP_MISS_NOFETCH
    An ICP_OP_MISS_NOFETCH response indicates that the requesting server may
    not request the named object from this server.  This may be because the
    origin server is under heavy load at the time or some other policy
    indicates that the request must not be forwarded at the moment.

The response (hit, miss, etc.) to a particular ICP query is based on one or
more configured policies.  The mechanics of defining and registering those
policies is explained in the next section.

This package does not implement the deprecated ICP_OP_HIT_OBJ.


Defining Policies
=================

To use this package one or more polices must be defined and registered.  The
Zope component architecture is used to manage the polices as "utilities".

Policies must implement the IICPPolicy interface.

    >>> from zc.icp.interfaces import IICPPolicy
    >>> IICPPolicy
    <InterfaceClass zc.icp.interfaces.IICPPolicy>

At this point no policy is registered, so any URL will generate a miss.

    >>> import zc.icp
    >>> zc.icp.check_url('http://example.com/foo')
    'ICP_OP_MISS'

Let's say we want to return an ICP_OP_HIT for all URLs containing "foo", we
can define that policy like so:

    >>> def foo_hit_policy(url):
    ...     if 'foo' in url:
    ...         return 'ICP_OP_HIT'

When registering this policy we have to provide an associated name.  Any
subsequent registration with the same name will override the previous
registration.  The default name is the empty string.

    >>> import zope.component
    >>> zope.component.provideUtility(foo_hit_policy, IICPPolicy, 'foo')

The registered policy is immediately available.

    >>> zc.icp.check_url('http://example.com/foo')
    'ICP_OP_HIT'

Non-foo URLs are still misses.

    >>> zc.icp.check_url('http://example.com/bar')
    'ICP_OP_MISS'

Now we can add another policy to indicate that we don't want any requests with
"baz" in them.

    >>> def baz_hit_policy(url):
    ...     if 'baz' in url:
    ...         return 'ICP_OP_MISS_NOFETCH'
    >>> zope.component.provideUtility(baz_hit_policy, IICPPolicy, 'baz')

    >>> zc.icp.check_url('http://example.com/foo')
    'ICP_OP_HIT'
    >>> zc.icp.check_url('http://example.com/bar')
    'ICP_OP_MISS'
    >>> zc.icp.check_url('http://example.com/baz')
    'ICP_OP_MISS_NOFETCH'

The policies are prioritized by name.  The first policy to return a non-None
result is followed.  Therefore if we check a URL with both "foo" and "baz" in
it, the policy for "baz" is followed.

    >>> zc.icp.check_url('http://example.com/foo/baz')
    'ICP_OP_MISS_NOFETCH'


Running the Server
==================

Starting the server begins listening on the given port and IP.

    >>> zc.icp.start_server('localhost', 3130)
    info: ICP server started
        Address: localhost
        Port: 3130

Now we can start sending ICP requests and get responses back.  To do so we must
first construct an ICP request.

    >>> import struct
    >>> query = zc.icp.HEADER_LAYOUT + zc.icp.QUERY_LAYOUT
    >>> url = 'http://example.com/\0'
    >>> format = query % len(url)
    >>> icp_request = struct.pack(
    ...     format, 1, 2, struct.calcsize(format), 0xDEADBEEF, 0, 0, 0, 0, url)
    >>> print zc.icp.format_datagram(icp_request)
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |  ICP_OP_QUERY |   Version: 2  |     Message Length: 44        |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |                    Request Number: DEADBEEF                   |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |                    Options: 0                                 |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |                    Option Data: 0                             |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |                    Sender Host Address: 0                     |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |                                                               |
    |    Payload: \x00\x00\x00\x00http://example.com/\x00           |
    |                                                               |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

After sending the request we get back a response.

    >>> import socket
    >>> s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    >>> s.connect(('localhost', 3130))

    >>> s.send(icp_request)
    44
    >>> icp_response = s.recv(16384)
    >>> icp_response
    '\x03\x02\x00(\xde\xad\xbe\xef\x00\x00\x00\x00\...http://example.com/\x00'
    >>> print zc.icp.format_datagram(icp_response)
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |  ICP_OP_MISS  |   Version: 2  |     Message Length: 40        |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |                    Request Number: DEADBEEF                   |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |                    Options: 0                                 |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |                    Option Data: 0                             |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |                    Sender Host Address: 0                     |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |                                                               |
    |    Payload: http://example.com/\x00                           |
    |                                                               |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

That was a miss.  We can also provoke a hit by satisfying one of our policies.

    >>> url = 'http://example.com/foo\0'
    >>> format = query % len(url)
    >>> icp_request = struct.pack(
    ...     format, 1, 2, struct.calcsize(format), 0xDEADBEEF, 0, 0, 0, 0, url)
    >>> print zc.icp.format_datagram(icp_request)
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |  ICP_OP_QUERY |   Version: 2  |     Message Length: 47        |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |                    Request Number: DEADBEEF                   |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |                    Options: 0                                 |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |                    Option Data: 0                             |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |                    Sender Host Address: 0                     |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |                                                               |
    |    Payload: \x00\x00\x00\x00http://example.com/foo\x00        |
    |                                                               |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

    >>> s.send(icp_request)
    47
    >>> print zc.icp.format_datagram(s.recv(16384))
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |  ICP_OP_HIT   |   Version: 2  |     Message Length: 43        |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |                    Request Number: DEADBEEF                   |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |                    Options: 0                                 |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |                    Option Data: 0                             |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |                    Sender Host Address: 0                     |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |                                                               |
    |    Payload: http://example.com/foo\x00                        |
    |                                                               |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
