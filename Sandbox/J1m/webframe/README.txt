A little web application for keeping an eye on things
======================================================

There are a lot of things I'd keep an eye on, if it was easier,
including:

- Nagios problem summaries
- Various plots showing metrics for our hosted applications
- finance.google.com
- social network feeds
- ...

I could keep web pages open, but that takes too much space.

What I want is the equivalent of an electronic photo frame for web
pages.

I decided to throw something together today that would do this for me:

   http://www.riversnake.com/webframe

This is a purely client side application that collects URLs and
cycles through them, staying on each one for a minute at a time.  You
can add, list and remove URLs.  You can stop and start cycling, move
forward and back, and select URLs to display.

There are a few interesting things to note:

Web Storage
  The localStorage facility provided by modern browsers is used to
  store the list of URLs.  The storage is keyed on the URL, so you can
  keep multiple lists of URLs by adding query strings (or copying the
  application to other URLs).

Layout
  The application has a row of controls across the top and an iframe
  that takes up the rest of the page.  Getting the iframe to fill the
  remainder of the page, and getting the URL bar at the top to fill
  the middle of the control bar was a bit tricky.  Using CSS
  percentage based sizes wasn't acceptable because I didn't want to
  scale all components equally when resizing a page (or when zooming
  in or out).

  The most common technique seems to be to use javascript handlers for
  page resizes to resize the page contents.  Dojo, which I used for
  the control widgets has some mechanisms to do this, but I wanted to
  see if I could manage it totally with CSS.

  I ended up using a combination of absolute and fixed positioning
  expressed in terms of ems. See the CSS styles in the HTML for more
  information.

Unicode Fun
  I was too lazy to go scrounge up images to use for the player
  controls, so I ended up using unicode text that got me close
  enough. :)



