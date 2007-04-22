#!/bin/bash
# release-egg.sh -- created 22-Apr-2007, <+NAME+>
# @Last Change: 24-Dez-2004.
# @Revision:    0.0
#!/bin/bash

svn_base="svn+ssh://svn.zope.org/repos/main"
distribution_target="download.zope.org:/distribution/"

package=${1}
version=${2}
branch="trunk"

if [ ! "${package}" ]; then
    echo "No package name given."
    exit;
fi

if [ ! "${version}" ]; then
    echo "No release version given."
    exit;
fi

tag_url="${svn_base}/${package}/tags/${version}"
trunk_url="${svn_base}/${package}/${branch}"

function update_versions() {
     mv setup.py setup.py.old
     cat setup.py.old | sed "s/version\W*=.*/version = '${1}',/" > setup.py
     rm setup.py.old
}

echo "Tagging release in repository at ${tag_url} ..."
read -p "[key to start]"
svn cp -m "Tagging ${version}" "${trunk_url}" "${tag_url}"

echo "Checking out tag ..."
svn co "${tag_url}" ${package}
cd "${package}"

echo "Updating version in setup.py ..."
update_versions "${version}"

echo "Committing version update ..."
svn status
svn diff
read -p "[key to start]"
svn commit -m "Updating version."

echo "Creating package ..."
read -p "[key to start]"
export COPY_EXTENDED_ATTRIBUTES_DISABLE=true
python setup.py egg_info -RDb "" sdist

echo "Uploading ..."
read -p "[key to start]"
scp dist/${package}-${version}.tar.gz ${distribution_target}

echo "Done"

# vi: 
