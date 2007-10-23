Creating Source Releases from Buildouts
=======================================

The zc.sourcerelease package provides a script,
buildout-source-release, that generates a source release from a
buildout.  The source release, in the form of a gzipped tar archive
[#zip_in_future]_.  The generated source release can be used as the
basis for higher-level releases, such as RPMs or
configure-make-make-install releases.

The source releases includes data that would normally be installed in
a download cache, such as Python distributions, or downloads performed
by the zc.recipe.cmmi recipe.  If a buildout uses a recipe that
downloads data but does not store the downloaded data in the buildout
download cache, then the data will not be included in the source
release and will have to be downloaded when the source release is
installed. 

The source release includes a Python install script.  It is not
executable and is run with the desired Python.  The install script
runs the buildout in place.  This means that
the source release will need to be extracted to and the buildout run
in the final install location [#separate_install_step]_.  While the
install script can be used directly, it will more commonly be used by
system-packaging (e.g. RPM) build scripts or make files.

To create a source release, simply run the buildout-source-release
script, passing a file URL or a subversion URL
[#other_source_code_control_systems]_ and the name of the
configuration file to use.  File URLs are useful for testing and can
be used with non-subversion source-code control systems.

Let's look at an example.  We have a server with some distributions on
it. 

    >>> print get(link_server),

We also have a sample buildout in which we'll install the
buildout-source-release script:

    >>> write('buildout.cfg', 
    ... '''
    ... [buildout]
    ... parts = script
    ... find-links = %(link_server)s
    ... 
    ... [script]
    ... recipe = zc.recipe.egg
    ... eggs = zc.sourcerelease
    ... ''' % globals())

    >>> print system(buildout), # doctest: +ELLIPSIS
    Getting distribution for 'zc.recipe.egg'.
    ...
    Generated script '/sample-buildout/bin/buildout-source-release'.


This just gets us the script.  Now we'll create another buildout that
we'll use for our source release.  

    >>> mkdir('sample')
    >>> sample = join(sample_buildout, 'sample')
    >>> write(sample, 'buildout.cfg', 
    ... '''
    ... [buildout]
    ... parts = sample
    ... find-links = %(link_server)s
    ... 
    ... [sample]
    ... recipe = zc.recipe.egg
    ... eggs = sample1
    ... ''' % globals())

We'll run the release script against this sample directory:

    >>> print system(join('bin', 'buildout-source-release')
    ...        +' file://'+join(sample)+' buildout.cfg'),

What we end up with is a tar file:

    >>> ls()

Let's copy the tar file to a temporary directory:

    >>> mkdir('test')
    >>> import tarfile
    >>> tf = tarfile.open('sample.tgz', 'r:gz')
    >>> tf.extract('sample', 'test')
    >>> ls('test')

.. [#zip_in_future] It is possible that an option will be added in the
future to generate zip files rather than tar archives.

.. [#separate_install_step] In the future, it is likely that we'll
also support a model in which the install script can install to a
separate location.  Buildouts will have to take this into account,
providing for copying necessary files, other than just scripts and
eggs, into the destination directory.

.. [#other_source_code_control_systems] Other source
code control systems may be supported in the future.
