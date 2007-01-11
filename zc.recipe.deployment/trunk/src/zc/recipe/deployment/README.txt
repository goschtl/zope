Unix Deployment Support
=======================

The zc.recope.deploymemt recipe provides support for deploying
applications with multiple processes on Unix systems.  It creates
directories to hold application instance configuration, log and
run-time files.  It also sets or reads options that can be read by
other programs to find out where to place files:

etc-directory
    The name of the directory where configurtion files should be
    placed.  This is /etc/NAME, where NAME is the deployment
    name. 

log-directory
    The name of the directory where application instances should write
    their log files.  This is /var/log/NAME, where NAME is
    the deployment name.

run-directory
    The name of the directory where application instances should put
    their run-time files such as pid files and inter-process
    communication socket files.  This is /var/run/NAME, where
    NAME is the deployment name.

rc-directory
    The name of the directory where run-control scripts should be
    installed. This is /etc/init.d.

The log and run directories are created in such a way that the 
directorie are owned by the user specified in the user option and are
writable by the user and the user's group.
