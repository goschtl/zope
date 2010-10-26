#!/bin/sh

builddocs()
{
cd $WORKDIR
RELEASE=$1
SVNFOLDER=$2
BUILDFOLDER=$3
# checkout or update trunk/tag
svn co $SVN/$SVNFOLDER $SOURCE/$BUILDFOLDER
# create html
$SPHINXBUILD -q -c $WORKDIR/$CONF -D release="$RELEASE" -D version="$RELEASE" \
             -b html $SOURCE/$BUILDFOLDER/doc/ $BUILD/$BUILDFOLDER
# create latex
$SPHINXBUILD -q -c $WORKDIR/$CONF -D release="$RELEASE" -D version="$RELEASE" \
             -b latex $SOURCE/$BUILDFOLDER/doc/ $BUILD/$BUILDFOLDER/latex
# create pdf
cd $BUILD/$BUILDFOLDER/latex
make all-pdf
# copy pdf files
cp tutorial.pdf ..
cp reference.pdf ../reference
}

# variables
WORKDIR=/var/www/build-html
CONF=conf
SOURCE=source
BUILD=/var/www/html/grok/doc
SPHINXBUILD=bin/sphinx-build

# constants
SVN=svn://svn.zope.org/repos/main/grok

# builddocs release svnfolder buildfolder
#  release: version/release name used in the docs
#  svnfolder: relative to svn://svn.zope.org/repos/main/grok
#  buildfolder: folder id for the built docs
builddocs 1.2.1 tags/1.2.1 1.2.1
builddocs 1.3dev trunk 1.3dev
#builddocs 1.0 tags/1.0 1.0
#builddocs 1.0b2 tags/1.0b2 1.0b2
#builddocs 1.0b1 tags/1.0b1 1.0b1
#builddocs 1.0a4 tags/1.0a4 1.0a4
#builddocs 0.14.1 tags/0.14.1 0.14.1
#builddocs 0.13.1 tags/0.13.1 0.13.1
