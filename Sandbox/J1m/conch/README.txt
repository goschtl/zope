
I really like the ssh architecture, especially from a usage point of
view.  You have ssh keys that you can use to authenticate against a
variety of services.  The SSH protocol provides both encrypted
connections and authentcation.  Conceptually, as a network
infrastructure seems to be easy to implement than SSL which requires
certificate authorities and requires additional authentication
infrastructure.

I've played with implementing custom ssh servers using paramiko in the
past. Lately, I've been plating with twisted.conch.  ZRS 2 uses
twisted and it might be interesting to provide replication over ssh.
In the future, I'd love to support ZEO over ssh for both
authentication (and someday, authorization) and encryption.

Wikipedia gives a nice high-level overview of the SSH architecture:

  http://en.wikipedia.org/wiki/Secure_Shell

I'd like to be able to implement application-specific network services
(e.g. ZRS or ZEO) as custom ssh channels. (I think it's pretty cool
that a server can provide multiple named services via channels. This
is potentially an alternative to integer ports, which are difficult to
manage.)

My current experiment provides a simple echo server and client that
communicate via a shell channel. The next iteration will use a custom
channel.
