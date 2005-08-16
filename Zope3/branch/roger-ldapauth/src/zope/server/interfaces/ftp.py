##############################################################################
# Copyright (c) 2002 Zope Corporation and Contributors.
# All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
##############################################################################
"""XXX short summary goes here.

XXX longer description goes here.

$Id$
"""
__metaclass__ = type

from zope.interface import Interface

class IFTPCommandHandler(Interface):
    """This interface defines all the FTP commands that are supported by the
       server.

       Every command takes the command line as first arguments, since it is
       responsible
    """

    def cmd_abor(args):
        """Abort operation. No read access required.
        """

    def cmd_appe(args):
        """Append to a file. Write access required.
        """

    def cmd_cdup(args):
        """Change to parent of current working directory.
        """

    def cmd_cwd(args):
        """Change working directory.
        """

    def cmd_dele(args):
        """Delete a file. Write access required.
        """

    def cmd_help(args):
        """Give help information. No read access required.
        """

    def cmd_list(args):
        """Give list files in a directory or displays the info of one file.
        """

    def cmd_mdtm(args):
        """Show last modification time of file.

           Example output: 213 19960301204320

           Geez, there seems to be a second syntax for this fiel, where one
           can also set the modification time using:
           MDTM datestring pathname

        """

    def cmd_mkd(args):
        """Make a directory. Write access required.
        """

    def cmd_mode(args):
        """Set file transfer mode.  No read access required. Obselete.
        """

    def cmd_nlst(args):
        """Give name list of files in directory.
        """

    def cmd_noop(args):
        """Do nothing. No read access required.
        """

    def cmd_pass(args):
        """Specify password.
        """

    def cmd_pasv(args):
        """Prepare for server-to-server transfer. No read access required.
        """

    def cmd_port(args):
        """Specify data connection port. No read access required.
        """

    def cmd_pwd(args):
        """Print the current working directory.
        """

    def cmd_quit(args):
        """Terminate session. No read access required.
        """

    def cmd_rest(args):
        """Restart incomplete transfer.
        """

    def cmd_retr(args):
        """Retrieve a file.
        """

    def cmd_rmd(args):
        """Remove a directory. Write access required.
        """

    def cmd_rnfr(args):
        """Specify rename-from file name. Write access required.
        """

    def cmd_rnto(args):
        """Specify rename-to file name. Write access required.
        """

    def cmd_size(args):
        """Return size of file.
        """

    def cmd_stat(args):
        """Return status of server. No read access required.
        """

    def cmd_stor(args):
        """Store a file. Write access required.
        """

    def cmd_stru(args):
        """Set file transfer structure. Obselete."""

    def cmd_syst(args):
        """Show operating system type of server system.

           No read access required.

           Replying to this command is of questionable utility,
           because this server does not behave in a predictable way
           w.r.t. the output of the LIST command.  We emulate Unix ls
           output, but on win32 the pathname can contain drive
           information at the front Currently, the combination of
           ensuring that os.sep == '/' and removing the leading slash
           when necessary seems to work.  [cd'ing to another drive
           also works]

           This is how wuftpd responds, and is probably the most
           expected.  The main purpose of this reply is so that the
           client knows to expect Unix ls-style LIST output.

           one disadvantage to this is that some client programs
           assume they can pass args to /bin/ls.  a few typical
           responses:

           215 UNIX Type: L8 (wuftpd)
           215 Windows_NT version 3.51
           215 VMS MultiNet V3.3
           500 'SYST': command not understood. (SVR4)
        """

    def cmd_type(args):
        """Specify data transfer type. No read access required.
        """

    def cmd_user(args):
        """Specify user name. No read access required.
        """



# this is the command list from the wuftpd man page
# '!' requires write access
#
not_implemented_commands = {
        'acct':        'specify account (ignored)',
        'allo':        'allocate storage (vacuously)',
        'site':        'non-standard commands (see next section)',
        'stou':        'store a file with a unique name',                            #!
        'xcup':        'change to parent of current working directory (deprecated)',
        'xcwd':        'change working directory (deprecated)',
        'xmkd':        'make a directory (deprecated)',                            #!
        'xpwd':        'print the current working directory (deprecated)',
        'xrmd':        'remove a directory (deprecated)',                            #!
}


class IFileSystemAccess(Interface):
    """Provides authenticated access to a filesystem.
    """

    def authenticate(credentials):
        """Verifies filesystem access based on the presented credentials.

        Should raise Unauthorized if the user can not be authenticated.

        This method only checks general access and is not used for each
        call to open().  Rather, open() should do its own verification.

        Credentials are passed as username/password tuples.
        
        """

    def open(credentials):
        """Returns an IFileSystem.

        Should raise Unauthorized if the user can not be authenticated.

        Credentials are passed as username/password tuples.

        """


class IFileSystem(Interface):
    """We want to provide a complete wrapper around any and all read
       filesystem operations.

       Opening files for reading, and listing directories, should
       return a producer.

       All paths are POSIX paths, even when run on Windows,
       which mainly means that FS implementations always expect forward
       slashes, and filenames are case-sensitive.

       Note: A file system should *not* store any state!
    """

    def type(path):
        """Return the file type at path

        The return valie is 'd', for a directory, 'f', for a file, and
        None if there is no file at the path.

        This method doesn't raise exceptions.
        """

    def names(path, filter=None):
        """Return a sequence of the names in a directory

        If the filter is not None, include only those names for which
        the filter returns a true value.
        """

    def ls(path, filter=None):
        """Return a sequence of information objects

        Returm item info objects (see ls_info) for the files in a directory.

        If the filter is not None, include only those names for which
        the filter returns a true value.
        """
        return list(tuple(str, str))

    def readfile(path, outstream, start=0, end=None):
        """Outputs the file at path to a stream.

        Data are copied starting from start. If end is not None,
        data are copied up to end.
        
        """

    def lsinfo(path):
        """Return information for a unix-style ls listing for the path

        Data are returned as a dictionary containing the following keys:

        type

           The path type, either 'd' or 'f'.

        owner_name

           Defaults to "na". Must not include spaces.

        owner_readable

           defaults to True

        owner_writable

           defaults to True

        owner_executable

           defaults to True for directories and false otherwise.

        group_name

           Defaults to "na". Must not include spaces.

        group_readable

           defaults to True

        group_writable

           defaults to True

        group_executable

           defaults to True for directories and false otherwise.

        other_readable

           defaults to False

        other_writable

           defaults to False

        other_executable

           defaults to True for directories and false otherwise.

        mtime

           Optional time, as a datetime. 

        nlinks

           The number of links. Defaults to 1.

        size

           The file size.  Defaults to 0.

        name

           The file name.           
        """

    def mtime(path):
        """Return the modification time for the file

        Return None if it is unknown.
        """

    def size(path):
        """Return the size of the file at path
        """

    def mkdir(path):
        """Create a directory.
        """

    def remove(path):
        """Remove a file. Same as unlink.
        """

    def rmdir(path):
        """Remove a directory.
        """

    def rename(old, new):
        """Rename a file or directory.
        """

    def writefile(path, instream, start=None, end=None, append=False):
        """Write data to a file.

        If start or end is not None, then only part of the file is
        written. The remainder of the file is unchanged.
        If start or end are specified, they must ne non-negative.

        If end is None, then the file is truncated after the data are
        written.  If end is not None, parts of the file after end, if
        any, are unchanged.  If end is not None and there isn't enough
        data in instream to fill out the file, then the missing data
        are undefined.
        
        If neither start nor end are specified, then the file contents
        are overwritten.

        If start is specified and the file doesn't exist or is shorter
        than start, the file will contain undefined data before start.

        If append is true, start and end are ignored.
        """

    def writable(path):
        """Return boolean indicating whether a file at path is writable

        Note that a true value should be returned if the file doesn't
        exist but it's directory is writable.

        """
