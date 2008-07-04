Recipe for installing Perl packages via download
************************************************

The perlpackages recipe automates installation of Perl packages.

This recipe is similar to zc.recipe.cmmi, but instead of performing
"configure, make, make install" it uses "perl Makefile.PL" for the configure
step.

Options
-------

url
    Location to download the Perl distribution from.

extra_options
    Additional parameters that are passed to Makefile.PL.

perl
    Name of the Perl interpreter to use for "perl Makefile.PL". Defaults
    to "perl".

flatinstallprefix
    Set the installation prefix, and force all library, doc and bin files to
    be flattened into three install locations:
    
        ${flatinstallprefix}/lib/perl5/
        ${flatinstallprefix}/bin/
        ${flatinstallprefix}/man/

    This is suitable for creating a location that you can include in your
    PERL5LIB environment variable.
