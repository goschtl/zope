Name: zc.zopeorgkeyupload
Version: 0
Release: 0

Summary: svn.zope.org public key upload
License: ZPL
Group: Applications/Internet
Requires: cleanpython26
Requires: zaamdashboardapplication
Requires: zcuser-zope
BuildRequires: cleanpython26
BuildRequires: zaamdashboardapplication
%define python /opt/cleanpython26/bin/python

##########################################################################
# Lines below this point normally shouldn't change

%define _prefix /opt
%define source %{name}-%{version}

URL: http://www.zope.com
Vendor: Zope Corporation
Packager: Zope Corporation <sales@zope.com>
Source: %{source}.tgz
Prefix: %{_prefix}
BuildRoot: %{_tmppath}/%{name}-%{version}-root
AutoReqProv: no

%description
%{summary}

%prep
%setup -n %{source}

%build
%{python} install.py bootstrap
%{python} install.py buildout:extensions=
eggs="develop-eggs eggs"
for egglink in develop-eggs/*.egg-link
do
    sed -i.bak -e "s|${RPM_BUILD_DIR}/%{source}|%{_prefix}/%{name}|" ${egglink}
    rm -f ${egglink}.bak
    src=$(sed -n -e "\|%{_prefix}/%{name}/|s|||p" ${egglink})
    eggs="${eggs} ${src}"
done
for dir in ${eggs}
do
    %{python} -m compileall -q -f -d %{_prefix}/%{name}/${dir} ${dir} || true
    %{python} -Om compileall -q -f -d %{_prefix}/%{name}/${dir} ${dir} || true
done

%install
to_remove="install.py release-distributions sbo"
for part in ${to_remove}
do
    rm -rf ${part}
done
rm -rf ${RPM_BUILD_ROOT}%{_prefix}/%{name}
mkdir -p ${RPM_BUILD_ROOT}%{_prefix}/%{name}
cp -a . ${RPM_BUILD_ROOT}%{_prefix}/%{name}

%clean
rm -rf ${RPM_BUILD_ROOT}

%files
%defattr(-, root, root)
%{_prefix}/%{name}
