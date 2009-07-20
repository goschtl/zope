#!/bin/bash
#
# The `fix-copyright` can be obtained by easy_installing `gocept.devtools`.
#
set -e

PROJECT="$1"
BASEURL="svn+ssh://svn.zope.org/repos/main/${PROJECT}"
FIXSCRIPT="fix-copyright"

usage() {
    cat <<__EOT__
Usage: $0 projectname

Fixes the copyright owner for a zope.org project.
Updates the trunk and the two most recent release branches.
__EOT__
}

function fix_one() {
    local url="$1"
    local workdir="${PROJECT}-copyrightfix"
    echo "Fixing ${url}"
    svn -q co ${url} ${workdir}
    ${FIXSCRIPT} --owner "Zope Foundation and Contributors." ${workdir}
    local remaining=$(egrep -niIr "Copyright \(c\).*Zope Corporation" ${workdir} | wc -l)
    if [[ ${remaining} != 0 ]]; then
        echo "ERROR: ${remaining} unfixed copyright lines remaining for ${url}"
        egrep -niIr "Copyright \(c\).*Zope Corporation" ${workdir}
        exit
    fi
    svn -q commit ${workdir} \
        -m "Updating copyright header after transfer of ownership to the Zope Foundation"
    rm -rf ${workdir}
}

function list_release_branches() {
    for branch in $(svn ls "${BASEURL}/branches"); do
        if [[ ${branch} =~ ^[0-9\.]+/$ ]]; then
            echo "${BASEURL}/branches/${branch}"
        fi
    done
}

function choose_branches() {
    list_release_branches | sort -n | tail -n 2
}

if [[ -n ${project} ]]; then
    usage
else
    fix_one "${BASEURL}/trunk"
    for branch in $(choose_branches); do
        fix_one ${branch}
    done
fi
