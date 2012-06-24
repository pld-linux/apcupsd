#
# Conditional build:
%bcond_with	usb	# with USB support
#
Summary:	Power management software for APC UPS hardware
Summary(pl):	Oprogramowanie do zarz�dzania energi� dla UPS-�w APC
Name:		apcupsd
Version:	3.10.15
Release:	1
License:	GPL v2
Group:		Networking/Daemons
Source0:	http://dl.sourceforge.net/apcupsd/%{name}-%{version}.tar.gz
# Source0-md5:	21b2b744ebcaa0010367a403a9c5e66c
Source1:	%{name}.init
Source2:	%{name}.logrotate
Patch0:		%{name}-configure.patch
URL:		http://www.apcupsd.com/
BuildRequires:	autoconf
Requires(post,preun):	/sbin/chkconfig
Requires(post):	fileutils
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sysconfdir	/etc/apcupsd

%description
UPS power management under Linux for APCC Products. It allows your
computer/server to run during power problems for a specified length of
time or the life of the batteries in your BackUPS, BackUPS Pro,
SmartUPS v/s, or SmartUPS, and then properly executes a controlled
shutdown during an extended power failure.

%description -l pl
Oprogramowanie do zarz�dzania energi� dla UPS-�w APC. Pozwala
komputerowi dzia�a� po awarii zasilania przez okre�lony czas lub czas
�ycia akumulator�w w BackUPS, BackUPS Pro, SmartUPS v/s, SmartUPS oraz
odpowiednio uruchamia kontrolowany shutdown przy d�u�szej awarii
zasilania.

%prep
%setup -q
%patch0 -p1

%build
cd autoconf
cp -f /usr/share/automake/config.sub .
%{__autoconf}
cp -f ./configure ..
cd ..
%configure \
	--with-log-dir=%{_var}/log \
	--with-stat-dir=%{_var}/lib/apcupsd \
%if %{with usb}
	--enable-usb \
	--with-serial-dev=/dev/usb/hiddev[0-15] \
	--with-upstype=usb \
	--with-upscable=usb
%endif

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/etc/{apcupsd,logrotate.d,rc.d/init.d} \
	$RPM_BUILD_ROOT/var/{log,lib/apcupsd}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/apcupsd
install %{SOURCE2} $RPM_BUILD_ROOT/etc/logrotate.d/apcupsd

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
if [ -f /var/lock/subsys/apcupsd ]; then
        /etc/rc.d/init.d/apcupsd restart >&2
else
	echo "Run \"/etc/rc.d/init.d/apcupsd start\" to start apcupsd daemon."
fi

%preun
if [ "$1" = "0" ]; then
	if [ -f /var/lock/subsys/apcupsd ]; then
		/etc/rc.d/init.d/apcupsd stop >&2
	fi
/sbin/chkconfig --del apcupsd
fi

%files
%defattr(644,root,root,755)
%doc ChangeLog Developers doc/{README.apcaccess,README.solaris}
%{_mandir}/man8/apcupsd.*
%attr(755,root,root) %{_sbindir}/*
%attr(640,root,root) %config(noreplace) %verify(not md5 size mtime) %{_sysconfdir}/apcupsd.conf
%attr(754,root,root) %{_sysconfdir}/apccontrol
%attr(754,root,root) %{_sysconfdir}/changeme
%attr(754,root,root) %{_sysconfdir}/commfailure
%attr(754,root,root) %{_sysconfdir}/commok
%attr(754,root,root) %{_sysconfdir}/mainsback
%attr(754,root,root) %{_sysconfdir}/masterconnect
%attr(754,root,root) %{_sysconfdir}/mastertimeout
%attr(754,root,root) %{_sysconfdir}/onbattery
%attr(754,root,root) /etc/rc.d/init.d/apcupsd
%attr(754,root,root) /etc/rc.d/init.d/halt
%attr(640,root,root) /etc/logrotate.d/apcupsd
%dir /etc/apcupsd
%dir /var/lib/apcupsd
%attr(640,root,root) %ghost /var/log/apcupsd.events
%attr(640,root,root) %ghost /var/lib/apcupsd/apcupsd.status
