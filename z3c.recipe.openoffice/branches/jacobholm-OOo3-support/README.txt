z3c.recipe.openoffice
=====================

    This recipe download openoffice in your buildout, it can also (optional)
    create egg with pyuno and change the default python used by openoffice.

    More info about Python UNO: http://udk.openoffice.org/python/python-bridge.html

    We are using this to generate OpenOffice documents from zope/python

Buildout configuration:
-----------------------

    Add this section to your buildout configuration::

        [buildout]
        parts =
            ... your other parts ...
            openoffice
        ...

        [openoffice]
        recipe = z3c.recipe.openoffice

    This will just download and install openoffice in your buildout

    To create the pyuno egg add the fallowing config::

        [openoffice]
        recipe = z3c.recipe.openoffice
        install-pyuno-egg = yes

    To also change openoffice python, add the following config::

        [openoffice]
        recipe = z3c.recipe.openoffice
        install-pyuno-egg = yes
        hack-openoffice-python = yes

    By default it will fetch version OpenOffice 2.3 but you might want to install from another location or another version like this::

        [openoffice]
        recipe = z3c.recipe.openoffice
        install-pyuno-egg = yes
        hack-openoffice-python = yes
        version = 2.3.1
        download-url = ftp://ftp.openoffice.skynet.be/pub/ftp.openoffice.org/stable/2.3.1/OOo_2.3.1_LinuxIntel_install_en-US.tar.gz

Notes:
------

    For this to work an OpenOffice process need to be running in background. As this require a X server and you don't want to install a real X server in a production environment you might want to use Xvfb. Here are the lines we use to start openoffice::

        $ cd myBuildout
        $ Xvfb :3 -ac -screen sn 800x600x16 &
        $ ./parts/openoffice/program/soffice "-accept=socket,host=localhost,port=2002;urp;" -display :3 &
        $ ./bin/instance start

    This recipe only works with linux at the moment

    To test pyuno (requires zopepy in buildout.cfg)::

        $ ./bin/zopepy
        >>> import pyuno

    If you get the fallowing error::

        "SystemError: dynamic module not initialized properly"

    Do::

        $ ldconfig YOURBUILDOUTFOLDER/parts/openoffice/program

    If you still face the same error, you might try::

        $  export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:"YOURBUILDOUTFOLDER/parts/openoffice/program"

    Be careful that the first time you will run soffice in server mode, openoffice will oblige you to pass throught a wizard run first openoffice on your
normal display or copy an .openoffice2 folder in the home of the user which is running the command.

    This recipe requires rpm2cpio and cpio to be installed on your system.

Authors:
--------

    Original author: Martijn Faassen - faassen@infrae.com

    Modified by: Jean-Francois Roche - jfroche@affinitic.be

