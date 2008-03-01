#
# Conditional build:
%bcond_without	test	# without TEST support
%bcond_without	usb	# without USB support
%bcond_without	net	# without network support
%bcond_without	cgi	# with CGI program support
%bcond_with	snmp	# with SNMP support
#
Summary:	Power management software for APC UPS hardware
Summary(pl.UTF-8):	Oprogramowanie do zarządzania energią dla UPS-ów APC
Name:		apcupsd
Version:	3.14.3
Release:	1
License:	GPL v2
Group:		Networking/Daemons
Source0:	http://dl.sourceforge.net/apcupsd/%{name}-%{version}.tar.gz
# Source0-md5:	a212351d21828e9344264614c7ad8ba1
Source1:	%{name}.init
Source2:	%{name}.logrotate
Source3:	%{name}.sysconfig
Patch0:		%{name}-configure.patch
URL:		http://www.apcupsd.com/
BuildRequires:	autoconf
BuildRequires:	gconfmm-devel
BuildRequires:	ncurses-ext-devel
%{?with_snmp:BuildRequires:	net-snmp-devel}
BuildRequires:	rpmbuild(macros) >= 1.268
Requires(post):	fileutils
Requires(post,preun):	/sbin/chkconfig
Requires:	rc-scripts
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sysconfdir	/etc/apcupsd
%define		_cgidir		/home/services/httpd/cgi-bin

%description
UPS power management under Linux for APCC Products. It allows your
computer/server to run during power problems for a specified length of
time or the life of the batteries in your BackUPS, BackUPS Pro,
SmartUPS v/s, or SmartUPS, and then properly executes a controlled
shutdown during an extended power failure.

%description -l pl.UTF-8
Oprogramowanie do zarządzania energią dla UPS-ów APC. Pozwala
komputerowi działać po awarii zasilania przez określony czas lub czas
życia akumulatorów w BackUPS, BackUPS Pro, SmartUPS v/s, SmartUPS oraz
odpowiednio uruchamia kontrolowany shutdown przy dłuższej awarii
zasilania.

%package cgi 
Summary:	upsstats - Web-based UPS status viewer
Summary(pl.UTF-8):	upsstats - oparta na WWW przeglądarka stanu UPS-a
Group:		Applications/Networking
Requires:	webserver

%description cgi
upsstats.cgi builds a lightweight web page containing basic UPS status
information.

%description cgi -l pl.UTF-8
upsstats.cgi tworzy lekką stronę WWW zawierającą podstawowe informacje
o stanie UPS-a.

%package gapcmon
Summary:	Apcupsd GUI monitoring application
Summary(pl.UTF-8):	Aplikacja GUI monitorowania Apcupsd
Group:		X11/Applications

%description gapcmon
Gnome/GTK based application which integrates into most desktop panels (not
just Gnome). It monitors one or more Apcupsd instances using Apcupsd's NIS
networking server. The status of each UPS is shown with a icon.

%description gapcmon -l pl.UTF-8
Oparta na Gnome/GTK aplikacja, która integruje się z panelami (nie tylko
Gnome). Monitoruje jedną bądź kilka instancji Apcupsd za pomocą serwera
NIS. Status każdego UPS-a przedstawia ikona.

%prep
%setup -q
%patch0 -p1
for i in configure.in aclocal.m4 config.h.in; do install autoconf/$i .;done

%build
%{__autoconf}
%configure \
	--with-log-dir=%{_var}/log \
	--with-stat-dir=%{_var}/lib/apcupsd \
%if %{with cgi}
	--enable-cgi \
	--with-cgi-bin=/home/services/httpd/cgi-bin \
%endif
	%{?with_test:--enable-test} \
%if %{with net}
	--enable-net \
%endif
	--enable-nls \
	--enable-powerflute \
	--enable-gapcmon \
	%{?with_snmp:--enable-snmp} \
	%{?with_usb:--enable-usb}

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/etc/{apcupsd,logrotate.d,rc.d/init.d,sysconfig} \
	$RPM_BUILD_ROOT/var/{log,lib/apcupsd}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install src/powerflute $RPM_BUILD_ROOT%{_sbindir}        
install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/apcupsd
install %{SOURCE2} $RPM_BUILD_ROOT/etc/logrotate.d/apcupsd
install %{SOURCE3} $RPM_BUILD_ROOT/etc/sysconfig/apcupsd

touch $RPM_BUILD_ROOT/var/log/apcupsd.events
touch $RPM_BUILD_ROOT/var/lib/apcupsd/apcupsd.status

cat > $RPM_BUILD_ROOT/etc/rc.d/init.d/halt << EOF
#!/bin/sh
/etc/rc.d/init.d/apcupsd powerdown
EOF

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add apcupsd
%service apcupsd restart "apcupsd daemon"

%preun
if [ "$1" = "0" ]; then
	%service apcupsd stop
	/sbin/chkconfig --del apcupsd
fi

%files
%defattr(644,root,root,755)
%doc ChangeLog Developers
%attr(755,root,root) %{_sbindir}/*
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/apcupsd.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/apcupsd
%attr(754,root,root) %{_sysconfdir}/apccontrol
%attr(754,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/changeme
%attr(754,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/commfailure
%attr(754,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/commok
#%attr(754,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/mainsback
%attr(754,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/onbattery
%attr(754,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/offbattery
%if %{with cgi}
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/hosts.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/multimon.conf
%{_sysconfdir}/apcupsd.css
%endif
%attr(754,root,root) /etc/rc.d/init.d/apcupsd
%attr(754,root,root) /etc/rc.d/init.d/halt
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/logrotate.d/apcupsd
%dir %{_sysconfdir}
%dir /var/lib/apcupsd
%attr(640,root,root) %ghost /var/log/apcupsd.events
%attr(640,root,root) %ghost /var/lib/apcupsd/apcupsd.status
%{_mandir}/man8/apcupsd.*

%files cgi
%defattr(644,root,root,755)
%attr(755,root,root) %{_cgidir}/*.cgi

%files gapcmon
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/*
%{_desktopdir}/gapcmon.desktop
%{_pixmapsdir}/*
