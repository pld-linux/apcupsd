Name:		apcupsd
Version:	3.8.1
Release:	2
License:	GPL v2
Group:		Networking/Daemons
Group(pl):	Sieciowe/Serwery
Source0:	http://www.sibbald.com/apcupsd/download/apcupsd-3.8.1.tar.gz
#Patch0:		apcups-initscript.patch
#Patch1:		apcups-makefile.patch
#Patch2:		apcupsd-Makefile-fix.patch
Summary:	power management software for APC UPS hardware
URL:		http://www.sibbald.com/apcupsd/
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)
#Icon:		apcupsd-logo.xpm


%description
UPS power management under Linux for APCC Products. It allows your
computer/server to run during power problems for a specified length of
time or the life of the batteries in your BackUPS, BackUPS Pro,
SmartUPS v/s, or SmartUPS, and then properly executes a controlled
shutdown during an extended power failure.

%prep
%setup -q
#%patch0 -p1
#%patch1 -p1
#%patch2 -p0

%build

%configure # --prefix=/usr --sbindir=/sbin --with-cgi-bin=/etc/apcupsd/cgi --enable-cgi 
%{__make}

#mv Makefile Makefile.orig
#cat Makefile.orig \
# | sed "s,^PREFIX    =,PREFIX    = ${RPM_BUILD_ROOT},"  \
# | sed "s,^MANPREFIX = /usr,MANPREFIX = ${RPM_BUILD_ROOT}/usr," \
# > Makefile
#%{__make} linux

%install
rm -rf $RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT{%{_sbindir},%{_bindir},%{_mandir}/man8,/etc/apcupsd/,/etc/rc.d/init.d,/var/log}

install apcupsd apcnetd $RPM_BUILD_ROOT%{_sbindir}
install apcaccess $RPM_BUILD_ROOT%{_bindir}
install etc/* $RPM_BUILD_ROOT/etc/apcupsd
install distributions/redhat/apccontrol.sh $RPM_BUILD_ROOT/etc/apcupsd/apccontrol
install distributions/redhat/apcupsd  $RPM_BUILD_ROOT/etc/rc.d/init.d/apcupsd
install doc/apcupsd.man $RPM_BUILD_ROOT%{_mandir}/man8
tar czf doc.tar.gz doc

#[ -x /sbin/powersc ] && /sbin/powersc RESTARTME
touch ${RPM_BUILD_ROOT}/var/log/apcupsd.log
touch ${RPM_BUILD_ROOT}%{_sysconfdir}/apcupsd.status

%clean
rm -rf ${RPM_BUILD_ROOT}

%post
/sbin/ldconfig
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


%preun
chkconfig --del apcupsd

%files
%defattr(644,root,root,755)
%doc doc.tar.gz 
%doc ChangeLog 
%{_mandir}/man8/apcupsd.*
%attr(755,root,root) %{_sbindir}/*
%attr(755,root,root) %{_bindir}/*
#%attr(755,root,root) %config /sbin/powersc
%attr(640,root,root) %config(noreplace) %{_sysconfdir}/apcupsd/apcupsd.conf
%attr(754,root,root) /etc/rc.d/init.d/apcupsd
%ghost /var/log/apcupsd.log
%ghost %{_sysconfdir}/apcupsd.status
