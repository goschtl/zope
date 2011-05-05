=================================
Creating SSH tunnels in buildouts
=================================

This recipe creates a control script for an SSH tunnel.  This is only
expected to work on systems with the OpenSSH "ssh" binary on $PATH,
and may require setting up the SSH configuration to use the expected
usernames for each system.

Let's create a configuration that defines a single tunnel in a part
called "my-tunnel"::

  >>> write("buildout.cfg", """\
  ...
  ... [buildout]
  ... parts = my-tunnel
  ... find-links = http://download.zope.org/distribution/
  ...
  ... [my-tunnel]
  ... recipe = zc.sshtunnel
  ... python = sample-python
  ... specification = 8080:server.example.net:6060
  ... via = somehost.example.net
  ...
  ... [sample-python]
  ... executable = /usr/bin/python
  ...
  ... """)

Building this out creates a single script in the bin/ directory::

  >>> print system(join("bin", "buildout")),
  Installing my-tunnel

  >>> ls("bin")
  -  buildout
  -  my-tunnel

The script is a Python script; the tunnel parameters are stored at the
top of the script::

  >>> cat(join("bin", "my-tunnel"))
  #!/usr/bin/python
  ...
  pid_file = "/sample-buildout/parts/my-tunnel.pid"
  specification = "8080:server.example.net:6060"
  via = "somehost.example.net"
  wait_port = 8080
  name = "my-tunnel"
  ...

The script accepts the "start", "stop", "restart", and "status"
verbs.  Let's demonstrate "status", since that doesn't require
actually establishing a tunnel::

  >>> print system(join("bin", "my-tunnel") + " status")
  Pid file /sample-buildout/parts/my-tunnel.pid doesn't exist
  <BLANKLINE>
