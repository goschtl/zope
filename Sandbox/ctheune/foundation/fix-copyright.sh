#!/bin/bash
set -e

# What happens if we run the fix script but no changes are there? (E.g. due to
# a re-run? IN this case we should also  not commit (check output of svn
# stat?)

PROJECT="$1"
BASEURL="svn+ssh://svn.zope.org/repos/main/${PROJECT}"
FIXSCRIPT="fix-copyright"
EXIT=""

usage() {
    cat <<__EOT__
Usage: $0 <projectname>
Update the copyright owner for a zope.org project to the Zope Foundation by
updating the trunk and the two most recent release branches.

Checks out the branches that are recommended to update and commits
automatically if all changes applied cleanly.

If any anomalies are detected the checkout remains in the current working
directory. You can then fix the reported errors and re-run the script which
will cause the existing checkouts to be re-used.

<project> is the name of the project as found in the zope.org repository
(e.g. zope.publisher)

__EOT__
}

require_devtools() {
    cat <<__EOT__
    ERROR: The 'fix-copyright' script is missing. It can be obtained by
    easy_installing the egg 'gocept.devtools'.
__EOT__
}

function fix_one() {
    local url="$1"
    local tag="$2"
    local workdir="${PROJECT}-copyrightfix/${tag}"
    echo
    echo "Fixing ${url}"
    if [[ ! -a ${workdir} ]]; then
        svn -q co ${url} ${workdir}
    fi
    ${FIXSCRIPT} --year $(date +%Y) --owner "Zope Foundation and Contributors." ${workdir}
    sed "s/^\(.*\)author=['|\"].*['|\"]\(.*\)$/\1author='Zope Foundation and Contributors'\2/" <${workdir}/setup.py >${workdir}/setup.py.tmp
    mv ${workdir}/setup.py.tmp ${workdir}/setup.py
    egrep -A 1 -niIr "Copyright \(c\)" ${workdir}
    echo "Please check the copyright headers above and press [RETURN] to commit"
    read
    local changes=$(svn stat ${workdir}|egrep "^M"|wc -l)
    if [[ $changes -gt 0 ]]; then
        svn commit ${workdir} \
            -m "Updating copyright header after transfer of ownership to the Zope Foundation"
    else
        echo "Nothing to commit."
    fi
    rm -rf ${workdir}
}

function list_release_branches() {
    for branch in $(svn ls "${BASEURL}/branches"); do
        if [[ ${branch} =~ ^[0-9\.]+/$ ]]; then
            # Remove trailing slash in branch name
            echo "${branch/\//}"
        fi
    done
}

function choose_branches() {
    list_release_branches | sort -n | tail -n 2
}

if [[ -z ${PROJECT} ]]; then
    usage
    EXIT=1
fi

if [[ -z `which fix-copyright` ]]; then
    require_devtools
    EXIT=1
fi

if [[ -n $EXIT ]]; then
    exit $EXIT
fi

fix_one "${BASEURL}/trunk" "trunk"
for branch in $(choose_branches); do
    fix_one "${BASEURL}/branches/${branch}" "${branch}"
done

workingdirs=$(ls ${PROJECT}-copyrightfix)
if [[ -z $workingdirs ]]; then
    rm -r ${PROJECT}-copyrightfix
fi
