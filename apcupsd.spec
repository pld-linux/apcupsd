# TODO:
# - update paths and pld patches
# - avoid messing in halt script in %post
Summary:	Power management software for APC UPS hardware
Summary(pl):	Oprogramowanie do zarz±dzania energi± dla UPS-ów APC
Name:		apcupsd
Version:	3.10.5
Release:	0.1
License:	GPL v2
Group:		Networking/Daemons
Source0:	http://dl.sourceforge.net/apcupsd/%{name}-%{version}.tar.gz
Patch0:		%{name}-paths.patch
Patch1:		%{name}-pld.patch
#Patch1:	apcups-makefile.patch
#Patch2:	%{name}-Makefile-fix.patch
URL:		http://www.apcupsd.com/
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
#%patch0 -p1	-- configure should be patched to move files from /var/log to /var/lib
#%patch1 -p1	-- probably should be updated
#%patch2 -p0

%build
%configure2_13
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
#install -d $RPM_BUILD_ROOT{/etc/rc.d/init.d,/var/log,/var/lib/apcupsd}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install platforms/redhat/apcupsd $RPM_BUILD_ROOT/etc/rc.d/init.d/apcupsd
#install platforms/pld/apcupsd  $RPM_BUILD_ROOT/etc/rc.d/init.d/apcupsd

touch $RPM_BUILD_ROOT/var/log/apcupsd.log
touch $RPM_BUILD_ROOT/var/lib/apcupsd/apcupsd.status
touch $RPM_BUILD_ROOT/var/lib/apcupsd/apcupsd.events

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add apcupsd

#if !(grep /sbin/powersc /etc/rc.d/init.d/halt > /dev/null); then
cp -f /etc/rc.d/init.d/halt /etc/rc.d/init.d/halt.rpmorig
#sed -e '/# Now halt or reboot./i\' \
#     -e '\
# See if this is a powerfail situation.\

echo '
if [ -f /etc/apcupsd/powerfail ]; then\
  echo "APCUPSD to the Rescue!"\
  echo\
  /etc/apcupsd/apccontrol killpower \
  echo\
  sleep 120\
  exit 1\
fi\
' >  /etc/rc.d/init.d/halt
#' /etc/rc.d/init.d/halt.rpmorig > /etc/rc.d/init.d/halt
#fi
chmod 754 /etc/rc.d/init.d/halt

%preun
if [ "$1" = "0" ]; then
	/sbin/chkconfig --del apcupsd
fi

%files
%defattr(644,root,root,755)
%doc ChangeLog Developers doc/{README.apcaccess,developers_manual,home-page,logo,manual}
%{_mandir}/man8/apcupsd.*
%attr(755,root,root) %{_sbindir}/*
#%attr(755,root,root) %config /sbin/powersc
%attr(640,root,root) %config(noreplace) %{_sysconfdir}/apcupsd.conf
%attr(754,root,root) /etc/rc.d/init.d/apcupsd
%ghost /var/log/apcupsd.log
%ghost /var/lib/apcupsd/apcupsd.status
%ghost /var/lib/apcupsd/apcupsd.events
