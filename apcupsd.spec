#
# Conditional build:
%bcond_with	usb	# with USB support
#
Summary:	Power management software for APC UPS hardware
Summary(pl):	Oprogramowanie do zarz±dzania energi± dla UPS-ów APC
Name:		apcupsd
Version:	3.10.12
Release:	0.9
License:	GPL v2
Group:		Networking/Daemons
Source0:	http://dl.sourceforge.net/apcupsd/%{name}-%{version}.tar.gz
# Source0-md5:	4c35774d587c54276cf03926768ad551
Source1:	%{name}.init
Source2:	%{name}.logrotate
Source10:	%{name}-rc.d-halt
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
Oprogramowanie do zarz±dzania energi± dla UPS-ów APC. Pozwala
komputerowi dzia³aæ po awarii zasilania przez okre¶lony czas lub czas
¿ycia akumulatorów w BackUPS, BackUPS Pro, SmartUPS v/s, SmartUPS oraz
odpowiednio uruchamia kontrolowany shutdown przy d³u¿szej awarii
zasilania.

%prep
%setup -q
%patch0 -p1	

%build
cd autoconf
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
install %{SOURCE10} $RPM_BUILD_ROOT/etc/rc.d/init.d/halt-apcupsd
install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/apcupsd
install %{SOURCE2} $RPM_BUILD_ROOT/etc/logrotate.d/apcupsd

touch $RPM_BUILD_ROOT/var/log/apcupsd.events
touch $RPM_BUILD_ROOT/var/lib/apcupsd/apcupsd.status

%clean
rm -rf $RPM_BUILD_ROOT

%post
if [ "$1" = "1" ]; then
    /sbin/chkconfig --add apcupsd
    if [ -e /etc/rc.d/init.d/halt ]; then
	mv -f /etc/rc.d/init.d/halt /etc/rc.d/init.d/halt.rpmorig
    fi
    ln -s /etc/rc.d/init.d/halt-apcupsd /etc/rc.d/init.d/halt
fi

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
    rm -f /etc/rc.d/init.d/halt
    if [ -e /etc/rc.d/init.d/halt.rpmorig ]; then
	mv -f /etc/rc.d/init.d/halt /etc/rc.d/init.d/halt.rpmorig
    fi
    /sbin/chkconfig --del apcupsd
fi

%files
%defattr(644,root,root,755)
%doc ChangeLog Developers doc/{README.apcaccess,developers_manual,home-page,logo}
%{_mandir}/man8/apcupsd.*
%attr(755,root,root) %{_sbindir}/*
%attr(640,root,root) %config(noreplace) %{_sysconfdir}/apcupsd.conf
%attr(754,root,root) %{_sysconfdir}/apccontrol
%attr(754,root,root) %{_sysconfdir}/changeme
%attr(754,root,root) %{_sysconfdir}/commfailure
%attr(754,root,root) %{_sysconfdir}/commok
%attr(754,root,root) %{_sysconfdir}/mainsback
%attr(754,root,root) %{_sysconfdir}/masterconnect
%attr(754,root,root) %{_sysconfdir}/mastertimeout
%attr(754,root,root) %{_sysconfdir}/onbattery
%attr(754,root,root) /etc/rc.d/init.d/apcupsd
%attr(754,root,root) /etc/rc.d/init.d/halt-apcupsd
%attr(640,root,root) /etc/logrotate.d/apcupsd
%dir /var/lib/apcupsd
%attr(640,root,root) %ghost /var/log/apcupsd.events
%attr(640,root,root) %ghost /var/lib/apcupsd/apcupsd.status
