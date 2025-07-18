#
# Conditional build:
%bcond_without	cgi	# CGI program support
%bcond_without	gapcmon	# gapcmon GUI
%bcond_without	net	# network support
%bcond_with	snmp	# SNMP support
%bcond_without	test	# TEST support
%bcond_without	usb	# USB support

Summary:	Power management software for APC UPS hardware
Summary(pl.UTF-8):	Oprogramowanie do zarządzania energią dla UPS-ów APC
Name:		apcupsd
Version:	3.14.14
Release:	1
License:	GPL v2
Group:		Networking/Daemons
Source0:	https://downloads.sourceforge.net/apcupsd/%{name}-%{version}.tar.gz
# Source0-md5:	cc8f5ced77f38906a274787acb9bc980
Source1:	%{name}.init
Source2:	%{name}.logrotate
Source3:	%{name}.sysconfig
Patch0:		%{name}-configure.patch
Patch1:		control-config.patch
Patch2:		format-security.patch
Patch3:		shutdown.patch
Patch4:		cxxld.patch
Patch5:		systemd.patch
Patch6:		fixgui.patch
Patch7:		nodbg.patch
URL:		http://www.apcupsd.com/
%{?with_gapcmon:BuildRequires:	GConf2-devel >= 2.0}
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	gd-devel
%{?with_gapcmon:BuildRequires:	gtk+2-devel >= 2:2.4.0}
BuildRequires:	libstdc++-devel
BuildRequires:	libwrap-devel
BuildRequires:	man-db
%{?with_snmp:BuildRequires:	net-snmp-devel}
BuildRequires:	pkgconfig
BuildRequires:	rpmbuild(macros) >= 1.647
BuildRequires:	util-linux
Requires:	rc-scripts
Requires:	systemd-units >= 0.38
Requires(post):	fileutils
Requires(post,preun):	/sbin/chkconfig
Requires(post,preun,postun):	systemd-units >= 38
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
URL:		https://gapcmon.sourceforge.net/
Requires:	gtk+2 >= 2:2.4.0

%description gapcmon
GNOME/GTK+ based application which integrates into most desktop panels
(not just GNOME). It monitors one or more Apcupsd instances using
Apcupsd's NIS networking server. The status of each UPS is shown with
a icon.

%description gapcmon -l pl.UTF-8
Oparta na GNOME/GTK+ aplikacja, która integruje się z panelami (nie
tylko Gnome). Monitoruje jedną bądź kilka instancji Apcupsd za pomocą
serwera NIS. Status każdego UPS-a przedstawia ikona.

%prep
%setup -q
%patch -P0 -p1
%patch -P1 -p1
%patch -P2 -p1
%patch -P3 -p1
%patch -P4 -p1
%patch -P5 -p1
%patch -P6 -p1
%patch -P7 -p1

%build
for i in configure.in aclocal.m4 config.h.in; do
	cp -pf autoconf/$i .
done
cp -pf %{_datadir}/automake/{config.guess,config.sub,install-sh,mkinstalldirs} autoconf
%{__autoconf}
%configure \
	APCUPSD_MAIL="/bin/mail" \
	SHUTDOWN="/sbin/shutdown" \
	WALL="%{_bindir}/wall" \
	--with-libwrap \
	--with-log-dir=%{_var}/log \
	--with-stat-dir=%{_var}/lib/apcupsd \
	--enable-apcsmart \
%if %{with cgi}
	--enable-cgi \
	--with-cgi-bin=/home/services/httpd/cgi-bin \
%endif
	--enable-dumb \
	%{?with_gapcmon:--enable-gapcmon} \
	%{?with_net:--enable-net} \
	--enable-pcnet \
	%{?with_snmp:--enable-snmp} \
	%{?with_test:--enable-test} \
	%{?with_usb:--enable-usb}

%{__make} \
	VERBOSE=2

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/etc/{apcupsd,logrotate.d,rc.d/init.d,sysconfig} \
	$RPM_BUILD_ROOT/var/{log,lib/apcupsd}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install -p %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/apcupsd
cp -p %{SOURCE2} $RPM_BUILD_ROOT/etc/logrotate.d/apcupsd
cp -p %{SOURCE3} $RPM_BUILD_ROOT/etc/sysconfig/apcupsd

# systemd support
install -p -D apcupsd.service $RPM_BUILD_ROOT%{systemdunitdir}/apcupsd.service
install -p -D apcupsd_shutdown $RPM_BUILD_ROOT%{systemdunitdir}-shutdown/apcupsd_shutdown

touch $RPM_BUILD_ROOT/var/log/apcupsd.events
touch $RPM_BUILD_ROOT/var/lib/apcupsd/apcupsd.status

cat > $RPM_BUILD_ROOT/etc/rc.d/init.d/halt << EOF
#!/bin/sh
exec /etc/rc.d/init.d/apcupsd powerdown
EOF

# no hal
%{__rm} $RPM_BUILD_ROOT%{_datadir}/hal/fdi/policy/20thirdparty/80-apcupsd-ups-policy.fdi

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add apcupsd
%service apcupsd restart "apcupsd daemon"
%systemd_post %{name}.service

%preun
if [ "$1" = "0" ]; then
	%service apcupsd stop
	/sbin/chkconfig --del apcupsd
fi
%systemd_preun %{name}.service

%postun
%systemd_reload

%files
%defattr(644,root,root,755)
%doc ChangeLog Developers ReleaseNotes
%attr(755,root,root) %{_sbindir}/apcaccess
%attr(755,root,root) %{_sbindir}/apctest
%attr(755,root,root) %{_sbindir}/apcupsd
%attr(755,root,root) %{_sbindir}/smtp
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/apcupsd.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/apcupsd
%attr(754,root,root) %{_sysconfdir}/apccontrol
%attr(754,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/changeme
%attr(754,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/commfailure
%attr(754,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/commok
#%attr(754,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/mainsback
%attr(754,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/onbattery
%attr(754,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/offbattery
%attr(754,root,root) /etc/rc.d/init.d/apcupsd
%attr(754,root,root) /etc/rc.d/init.d/halt
%{systemdunitdir}/%{name}.service
%attr(755,root,root) %{systemdunitdir}-shutdown/apcupsd_shutdown
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/logrotate.d/apcupsd
%dir %{_sysconfdir}
%dir /var/lib/apcupsd
%attr(640,root,root) %ghost /var/log/apcupsd.events
%attr(640,root,root) %ghost /var/lib/apcupsd/apcupsd.status
%{_mandir}/man8/apcupsd.8*
%{_mandir}/man8/apctest.8*
%{_mandir}/man8/apcaccess.8*
%{_mandir}/man8/apccontrol.8*
%{_mandir}/man5/apcupsd.conf.5*

%if %{with cgi}
%files cgi
%defattr(644,root,root,755)
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/hosts.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/multimon.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/apcupsd.css
%attr(755,root,root) %{_cgidir}/multimon.cgi
%attr(755,root,root) %{_cgidir}/upsfstats.cgi
%attr(755,root,root) %{_cgidir}/upsimage.cgi
%attr(755,root,root) %{_cgidir}/upsstats.cgi
%endif

%if %{with gapcmon}
%files gapcmon
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/gapcmon
%{_desktopdir}/gapcmon.desktop
%{_pixmapsdir}/apcupsd.png
%{_pixmapsdir}/charging.png
%{_pixmapsdir}/gapc_prefs.png
%{_pixmapsdir}/onbatt.png
%{_pixmapsdir}/online.png
%{_pixmapsdir}/unplugged.png
%endif
