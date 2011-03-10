Name: sbo
Version: 0
Release: 0

Summary: System Buildouts
Group: System
Requires: cleanpython26
BuildRequires: cleanpython26
%define python /opt/cleanpython26/bin/python

##########################################################################      
# Lines below this point normally shouldn't change                              

%define source %{name}-%{version}-%{release}

Copyright: ZVSL
Vendor: Zope Corporation
Packager: Zope Corporation <sales@zope.com>
AutoReqProv: no
Source: %{source}.tgz

%define opt /opt

%description
%{summary}

%prep
rm -rf $RPM_BUILD_DIR/%{source}
zcat $RPM_SOURCE_DIR/%{source}.tgz | tar -xvf -

%build
if [ -d /opt/%{name} ] ; then chmod -R +w /opt/%{name} ; fi
rm -rf /opt/%{name}
cp -r $RPM_BUILD_DIR/%{source} %{opt}/%{name}
%{python} %{opt}/%{name}/install.py bootstrap
%{python} %{opt}/%{name}/install.py buildout:extensions=
%{python} -m compileall -f %{opt}/%{name}/src
chmod -R -w %{opt}/%{name}

%post
cd /opt/%{name}
%{python} bin/buildout -oqU \
    buildout:parts=system \
    buildout:develop= \
    buildout:installed=

%preun
if [[ $1 -eq 0 ]]
then
    rm -f /usr/local/bin/sbo
fi

%files
%attr(-, root, root) /opt/%{name}
