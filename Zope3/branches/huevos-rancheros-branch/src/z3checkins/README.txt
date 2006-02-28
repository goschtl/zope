Zope 3 Checkins
===============

This is a Zope 3 product for keeping track of <zope3-checkins@zope.org> mailing
list.  It adds a new content object type: CheckinMessage.  You can upload all
messages from the mailing list to your Zope 3 instance with a simple procmail
rule, and then view the latest checkins in your Mozilla sidebar or any news
aggregator that supports RSS, e.g. Nautilus.

It is also quite usable for other checkin-tracking mailing lists.  However
since there is no single standard on how the messages should be formatted,
your mileage may vary.


Installation
------------

Start up Zope 3 and add a Checkin Folder. You will be presented with a form.

  - the first field is a description used for checkins.rss view
  - the second field is a URL to the traditional mailing list archive.
  - the third field is a list of icon definitions used for checkins to
    different parts of the source trees.  Each line should contain four
    fields:

      prefix  icon-name  alt-text  title

    prefix is matched against the beginning of the checkin directory (put
    longer, more specific prefixes first.  * is a catch-all prefix, and
    should be placed last).  Lines starting with # are ignored.

    icon-name is a Zope 3 resource name.  z3checkins comes with the following
    icons: zope3.png, product.png, message.png, branch.png.

    alt-text is a short alternate text

    title is a longer description, usually shown in a tooltip

You would use the following configuration for zope3-checkins@zope.org:

  RSS view description:
  Latest Zope 3 Checkins

  URL of mailing list:
  http://mail.zope.org/pipermail/zope3-checkins/

  Icon definitions:
  # prefix        icon        title   description
  Zope3/branches  branch.png  Branch  Zope 3 branch
  *               zope3.png   Z3      Zope 3 trunk

Then, go to the Metadata tab and set the title.

Now you can create Checkin Messages in that folder.  In the rest of this
document I assume Zope 3 is accessible at http://localhost:8080/ and that
the checkin folder is called 'zope3-checkins'.


Upload script
-------------

Here's an example of a shell script that uses curl to upload a file or a list
of files, each containing a single RFC822 mail message:

  #!/bin/sh
  for file in "$@"; do
      curl -F field.data=@- -F UPDATE_SUBMIT=Submit -s -S \
           -u username:password \
           http://localhost:8080/zope3-checkins/+/CheckinMessage \
           < "$file" > /dev/null
  done

Replace username:password with the username and password of a Zope 3 user that
has zope.ManageContent permission in the 'zope3-checkins' folder.

This script may be used to import archives in Maildir format.  Or you can
use formail or some other tool to split mbox folders available at
http://mail.zope.org/pipermail/zope3-checkins/


Procmail
--------

Add this to your .procmailrc to upload new messages automatically:

:0:
* ^List-Id:.*<zope3-checkins\.zope\.org>
| curl -F field.data=@- -F UPDATE_SUBMIT=Submit -s -S -u username:password \
       http://localhost:8080/zope3-checkins/+/CheckinMessage > /dev/null

Replace username:password with the username and password of a Zope 3 user that
has zope.ManageContent permission in the 'zope3-checkins' folder.


RSS feed
--------

Use the following URL to access last checkins in RSS format:

  http://localhost:8080/zope3-checkins/checkins.rss


Good luck,
Marius Gedminas
<marius@pov.lt>
