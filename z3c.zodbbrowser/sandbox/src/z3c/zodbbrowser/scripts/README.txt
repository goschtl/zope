======
README
======

Start scripts
-------------

We provide some start scripts which can be used for a special subversion trunk 
setup. This setup looks like:

<ProjectRoot>
  - Zope3
    - src
      - zope
        - app
  - src
    - z3c
      - zodbbrowser
    - z3c
      - xy
    - myproject
      -packages

The scripts runzodbbrowser.py and runzodbbrowser.bat in this folder can be used in
the <ProjectRoot> as a startscript for the ZODB Browser. Put this scripts
into the root if you use a similar setup. The script will automaticly asjust
the import path if you start the ZODB Browser.

Note: this script is only tested on my windows box, feel free to correct it
if it's not working on your *nix box.
