HTTP request/response recorder
==============================

zope.app.recorder lets you create functional doctests without relying on
third-party tools such as tcpwatch.

Quick Start
-----------

Add the following section to your zope.conf:

  <server>
    type RecordingHTTP
    address 8081
  </server>

Now go to http://localhost:8081/ and do whatever needs to be recorded.  When
done, go to http://localhost:8081/++etc++process/RecordedSessions.html and
download your recorded session as a ready-to-run functional doctest.

This tool can also be useful for other purposes, not just for creating
functional doctests.

To Do
-----

- Remove the unsuccessful attempt to make RecordedSessions use MappingStorage,
  unless someone has an idea how to make it work.

Ideas for Further Development
-----------------------------

- Refactor zope.app.testing.dochttp for easier reuse
- List recorded requests in batches
- Let users clear only selected requests
- Show the remote IP for each request, allow filtering by IP
- Show the authenticated user for each request
- See how zope.app.recorder breaks with HTTP pipelining/chunked transfer
  encoding, then fix it
