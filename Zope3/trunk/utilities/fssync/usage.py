##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

USAGE="""
Usage: %s [options] operation [arguments]

Options:
  -h / --help              -- print this help message
  -f / --fspath FILE       -- filename for the object
  -o / --objpath PATH      -- ZODB path for the object (checkout only)
  -d / --dbpath FILE       -- filename for the ZODB (Data.fs file)
  -s / --siteconfpath FILE -- filename for site.zcml (configuration file)
  -t / --type TYPE         -- type of new object (add only)

Operations:
  checkout -- initial copy from ZODB to filesystem
  update   -- subsequent incremental copy from ZODB to filesystem
  commit   -- incremental copy from filesystem to ZODB
  fcommit  -- forced commit
  diff     -- show differences between filesystem, original, and current ZODB
  add      -- add one or more files
  addtypes -- show the list of supported types

FULL DOCUMENTATION
----------------------------------------------------------------------------
checkout --- checks out ZODB object in filesystem
             example:
                $python sync.py -f /home/user/sandbox
                                -d /zope3/data.fs
                                -s /zope3/site.zcml
                                -o /foo/bar
                                checkout
                  'or'

                $python sync.py --fspath=/home/user/sandbox
                                   --dbpath=/zope3/data.fs
                                   --siteconfpath=/zope3/site.zcml
                                   --objpath=/foo/bar
                                   checkout

                This will download the "bar" folder along with it's contents
                into the /home/user/sandbox folder. In case if the "bar" module
                already exist in the sandbox it will be overwritten.
                Checkout generates the following output:
                UPDATING foldername
                U foldername/filename


update   --- updates the sandbox
             example:
                $python sync.py -f /home/user/sandbox/bar
                                -d /zope3/data.fs
                                -s /zope3/site.zcml
                                update
                  'or'

                $python sync.py --fspath=/home/user/sandbox/bar
                                --dbpath=/zope3/data.fs
                                --siteconfpath=/zope3/site.zcml
                                update

                This will update the contents of "bar" directory in
                the sandbox.

                An update can undergo various cases like :

                Case1 : When the contents of all the three Sandbox, Original
                        and ZODB for an object is same an update command won't
                        do any changes.

                Case2 : When the contents of the Sandbox and Original are same
                        but ZODB is different, an update command will overwrite
                        Sandbox and Original from ZODB and print the following:
                        U /path/filename.

                Case3 : When the contents of the Original and ZODB are same and
                        the Sandbox is different an update command won't do any
                        changes and print the following:
                        M /path/filename.
                        If the Sandbox contains conflict data the following is
                        printed:
                        C /path/filename.

                Case4 : This is a very unlikely case. When the contents of the
                        Sandbox and ZODB are same but the Original is different
                        an update command will overwrite the Original with the
                        ZODB and print the following:
                        U /path/filename.

                Case5 : When the contents of all the three Sandbox, Original
                        and ZODB are different, an update command will mearge
                        all the changes into the Sandbox and the Original is
                        overwitten by the ZODB and the following is printed:
                        Merging changes in /path/filename
                        In case of a conflict the conflict data is copied into
                        the Sandbox and the Original is overwitten by the ZODB
                        and the following is printed:
                        C Merging changes in /path/filename

                Conventionaly an update has to be done on the sandbox before
                running commit.

commit   --- A commit command copies data from the filesystem samdbox
             into the ZODB
             example:
                $python sync.py -f /home/user/sandbox/bar
                                -d /zope3/data.fs
                                -s /zope3/site.zcml
                                commit
                  'or'

                $python sync.py --fspath=/home/user/sandbox/bar
                                --dbpath=/zope3/data.fs
                                --siteconfpath=/zope3/site.zcml
                                commit

             Commit copies the Sandbox into Original and ZODB, if the ZODB
             and Original are same or there is no conflict data in the Sandbox
             and prints the following:
             /path/filename  <-- filename
             If the ZODB and Original are not same or the Sandbox
             contains conflict data a commit command won't do anything
             and will print the following:
             /path/filename Conflict, Uptodate checkin failed.


fcommit  --- This is a force commit. A fcommit command will forcefully
             copy Sandbox
             into Original and ZODB regardless of any constraints.
             example:
                $python sync.py -f /home/user/sandbox/bar
                                -d /zope3/data.fs
                                -s /zope3/site.zcml
                                fcommit
                  'or'

                $python sync.py --fspath=/home/user/sandbox/bar
                                --dbpath=/zope3/data.fs
                                --siteconfpath=/zope3/site.zcml
                                fcommit


diff     --- Difference between Three versions of an object

            -1 -- Sandbox and Original
            -2 -- Sandbox and ZODB
            -3 -- ZODB and Original

            A diff command will produce the difference of two objects
            in context output format.
            example:
                $python sync.py -2 /home/user/sandbox/bar
                                -d /zope3/data.fs
                                -s /zope3/site.zcml
                                diff
                  'or'

                $python sync.py -2 /home/user/sandbox/bar
                                --dbpath=/zope3/data.fs
                                --siteconfpath=/zope3/site.zcml
                                diff
            Default option is -1


addtypes --- Displays all the list of types that can be added to the ZODB
                 from the filesystem.
                 example:
                 $python sync.py addtypes


add      --- Adds objects to file system and saves it to the ZODB on
             commit.
             This command will give a list of all the available types
             that can be added.
             example:
                 $python sync.py -f /home/user/sandbox/bar
                                 -d /zope3/data.fs
                                 -s /zope3/site.zcml
                                 -t file
                                 add file1.html file2.txt file3.xyz
                    'or'

                $python sync.py --fspath=/home/user/sandbox/bar
                                --dbpath=/zope3/data.fs
                                --siteconfpath=/zope3/site.zcml
                                --type=file
                                add file1.html file2.txt file3.xyz

            This command will add file1.html, file2.txt, file3.xyz in
            the bar folder of the sandbox and on commit this will be
            checked in as file type objects in ZODB.
            If type is not specified with -t option then the types will
            be checked based on file extensions and only the valid type
            will be added to the sandbox.
            File/Folder names with spaces has to be enclosed withing quotes.


ENVIRONMENT VARIABLES
----------------------------------------------------------------------------

SYNCROOT     --- Path for the filesystem folder where the ZODB object
                 has to be checked out.If not set it takes the default
                 directory. Or can be specified with the --fspath or -f
                 option

ZODBPATH     --- Path where the Data.fs file exist in the filesystem.
                 if not set it takes the default is ../../Data.fs.
                 Or can be specified with the --dbpath or -d option.

SITECONFPATH --- Path for the site.zcml file.if not set it takes the
                 default is ../../site.zcml. Or can be specified with
                 the --siteconfpath or -s option.
"""
