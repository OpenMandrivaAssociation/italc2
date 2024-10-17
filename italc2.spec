%define debug_package %{nil}

%define 	libname %mklibname italc
%define 	italcgrp italc

Summary:	Intelligent Teaching And Learning with Computers - software for teachers
Name:		italc2
Version:	2.0.1
Release:	3
License:	GPLv2+
Group:		Networking/Remote access
Url:		https://italc.sourceforge.net/
Source0:	italc2-%{version}.tar.bz2
Source2:	italc-start_ica
Source3:	italc.sysconfig
Source5:	ica-autostart.desktop
Source6:	italc-launcher
BuildRequires:	cmake
BuildRequires:	qt4-linguist
BuildRequires:	jpeg-devel
BuildRequires:	pam-devel
BuildRequires:	qt4-devel
BuildRequires:	pkgconfig(openssl)
BuildRequires:	pkgconfig(xtst)
BuildRequires:	pkgconfig(zlib)

%description
iTALC is a use- and powerful didactical tool for teachers. It lets you view
and control other computers in your network in several ways. It supports Linux
and Windows 2000/XP/Vista.

Features:

* see what's going on in computer-labs by using overview mode and
  make snapshots
* remote-control computers to support and help other people
* show a demo (either in fullscreen or in a window) - the teacher's screen
  is shown on all student's computers in realtime
* lock workstations for moving undivided attention to teacher
* send text-messages to students
* powering on/off and rebooting computers per remote
* remote logon and logoff and remote execution of arbitrary commands/scripts
* home-schooling - iTALC's network-technology is not restricted to a subnet
  and therefore students at home can join lessons via VPN-connections just
  by installing iTALC client

Furthermore iTALC is optimized for usage on multi-core systems (by making
heavy use of threads). No matter how many cores you have, iTALC can make use
of all of them.

#----------------------------------------------------------------------------

%package client
Summary:	Software for iTALC-clients
Group:		Networking/Remote access

%description client
This package contains the software, needed by iTALC-clients.

See /usr/share/italc/doc/INSTALL for details on how to install and setup iTALC
in your network.

%files client
%{_bindir}/ica
%{_bindir}/start-ica
%{_bindir}/italc_auth_helper
%config %{_sysconfdir}/xdg/autostart/ica-autostart.desktop
%config(noreplace) %{_sysconfdir}/sysconfig/ica
%dir %{_sysconfdir}/settings
%dir "%{_sysconfdir}/settings/iTALC Solutions"
%config(missingok,noreplace) "%{_sysconfdir}/settings/iTALC Solutions/iTALC.conf"
%dir %{_sysconfdir}/italc/keys/private
%defattr(0440,root,%{italcgrp},0750)
%dir %{_sysconfdir}/italc/keys/private/teacher
%dir %{_sysconfdir}/italc/keys/private/admin
%dir %{_sysconfdir}/italc/keys/private/supporter
%dir %{_sysconfdir}/italc/keys/private/other
%ghost %attr(0440,root,%{italcgrp}) %config(noreplace) %{_sysconfdir}/italc/keys/private/teacher/key
%ghost %attr(0440,root,%{italcgrp}) %config(noreplace) %{_sysconfdir}/italc/keys/private/admin/key
%ghost %attr(0440,root,%{italcgrp}) %config(noreplace) %{_sysconfdir}/italc/keys/private/supporter/key
%ghost %attr(0444,root,%{italcgrp}) %config(noreplace) %{_sysconfdir}/italc/keys/public/teacher/key
%ghost %attr(0444,root,%{italcgrp}) %config(noreplace) %{_sysconfdir}/italc/keys/public/admin/key
%ghost %attr(0444,root,%{italcgrp}) %config(noreplace) %{_sysconfdir}/italc/keys/public/supporter/key

%pre client
%{_sbindir}/groupadd -r -f %{italcgrp} 2>/dev/null ||:

%post client
if
    getent group %{italcgrp} >/dev/null
then
    : OK group %{italcgrp} already present
else
    groupadd -r %{italcgrp} 2>/dev/null || :
fi

#----------------------------------------------------------------------------

%package master
Summary:	iTALC master software
Group:		Networking/Remote access
Requires:	%{libname} = %{EVRD}
Requires:	%{name}-client = %{EVRD}
Requires(post):	%{name}-client = %{EVRD}

%description master
This package contains the actual master-software for accessing clients.

See /usr/share/italc/doc/INSTALL for details on how to install and setup iTALC
in your network.

%files master
%doc AUTHORS COPYING ChangeLog INSTALL README TODO
%{_bindir}/italc
%{_bindir}/italc-launcher
%{_bindir}/imc
%{_datadir}/pixmaps/*

%post master
if
    getent group %{italcgrp} >/dev/null
then
    : OK group %{italcgrp} already present
else
    groupadd -r %{italcgrp} 2>/dev/null || :
fi

# dont run scripts on update
if [ ${1:-0} -lt 2 ]; then
  for role in admin supporter teacher; do
	if [ ! -f "%{_sysconfdir}/italc/keys/private/$role/key" ]; then
		/usr/bin/ica -role $role -createkeypair 1>/dev/null
		chgrp %{italcgrp} "%{_sysconfdir}/italc/keys/private/$role/key"
		chmod 0440 "%{_sysconfdir}/italc/keys/private/$role/key"
	fi
  done
fi

#----------------------------------------------------------------------------

%package -n %{libname}
Summary:	Library used by ITALC
Group:		Networking/Remote access

%description -n %{libname}
iTALC is a use- and powerful didactical tool for teachers. It lets you
view and control other computers in your network in several ways. It
supports Linux and Windows 2000/XP/Vista and it even can be used
transparently in mixed environments!

This is a library used by %{name}-master and %{name}-client.

%files -n %{libname}
%doc AUTHORS COPYING ChangeLog INSTALL README TODO
%{_libdir}/*

#----------------------------------------------------------------------------

%prep
%setup -q

%build
%cmake_qt4
%make

%install
mkdir -p %{buildroot}%{_defaultdocdir}/%{name}

%makeinstall_std -C build
# create the directories containing the auth-keys
mkdir -p %{buildroot}%{_sysconfdir}/italc/keys/{private,public}/{teacher,admin,supporter,other}
# create pseudo key files so RPM can own them (ghost files)
for role in admin supporter teacher; do
	touch %{buildroot}%{_sysconfdir}/italc/keys/{private,public}/$role/key
done
# create the initial config
mkdir -p "%{buildroot}/%{_sysconfdir}/settings/iTALC Solutions"
cat > "%{buildroot}/%{_sysconfdir}/settings/iTALC Solutions/iTALC.conf" << EOF
[keypathsprivate]
admin=%{_sysconfdir}/italc/keys/private/admin/key
supporter=%{_sysconfdir}/italc/keys/private/supporter/key
teacher=%{_sysconfdir}/italc/keys/private/teacher/key

[keypathspublic]
admin=%{_sysconfdir}/italc/keys/public/admin/key
supporter=%{_sysconfdir}/italc/keys/public/supporter/key
teacher=%{_sysconfdir}/italc/keys/public/teacher/key
EOF
# install start script for ica client
install -D -m755 %{SOURCE2} %{buildroot}/%{_bindir}/start-ica
install -D -m644 %{SOURCE5} %{buildroot}/%{_sysconfdir}/xdg/autostart/ica-autostart.desktop
install -D -m755 %{SOURCE6} %{buildroot}/%{_bindir}/italc-launcher
# icon for the desktop file
install -Dm644 ima/data/italc.png %{buildroot}/%{_datadir}/pixmaps/italc.png
#
# Distribution specific
#
# configuration for ica

install -D -m644 %{SOURCE3} %{buildroot}/%{_sysconfdir}/sysconfig/ica

