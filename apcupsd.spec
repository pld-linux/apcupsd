Summary:	APC UPS Daemon.
Summary(pl):	APC UPS demon.
Name:		apcupsd
Version:	3.5.8
Release:	1
Copyright:	GPL
Group:		Daemons
Group(pl):	Demony	
Source:		http://www.brisse.dk/site/apcupsd/download/%{name}-%{version}.src.tar.gz
Patch0:		apcups-initscript.patch
Patch1:		apcups-Makefile.fix
Patch2:		apcups-inetd.patch
BuildRoot:	/tmp/%{name}-root

%define	_prefix	/
%define	_mandir	/usr/share/man

%description
UPS power management under Linux for APCC Products.
It allows your computer/server to run during power problems
for a specified length of time or the life of the batteries
in your BackUPS, BackUPS Pro, SmartUPS v/s, or SmartUPS, and
then properly executes a controlled shutdown during an
extended power failure.

%description -l pl

%prep
%setup -q -n %{name}-%{version}.src
%patch0 -p1
%patch1 -p0
%patch2 -p1

%build
make linux \
	MANPREFIX=$RPM_BUILD_ROOT%{_mandir} \
	CFLAGS="$RPM_OPT_FLAGS -I./include"

%install

install -d $RPM_BUILD_ROOT{%{_sysconfdir}/rc.d/init.d,%{_bindir},%{_sbindir},%{_mandir}/man8,/var/log}

install installs/apcupsd.conf $RPM_BUILD_ROOT%{_sysconfdir}

install -s apcupsd-linux $RPM_BUILD_ROOT%{_sbindir}/apcupsd
install -s apcaccess-linux $RPM_BUILD_ROOT%{_bindir}/apcaccess

install installs/powersc $RPM_BUILD_ROOT%{_sbindir}

install docs/apcupsd.man8 $RPM_BUILD_ROOT%{_mandir}/man8/apcupsd.8

install apcupsd ${RPM_BUILD_ROOT}/etc/rc.d/init.d/apcupsd

touch ${RPM_BUILD_ROOT}/var/log/apcupsd.log
touch ${RPM_BUILD_ROOT}/etc/apcupsd.status

gzip -9fn $RPM_BUILD_ROOT%{_mandir}/man8/*

%clean
rm -rf ${RPM_BUILD_ROOT}

%post
/sbin/chkconfig --add apcupsd

%preun
/sbin/chkconfig --del apcupsd

%files
%defattr(644, root, root,755)
%doc README.NEW Changelog port.gif Statement.APCC
%attr(644, root, root) %{_mandir}/man8/apcupsd.8.gz
%attr(755, root, bin)  %{_sbindir}/apcupsd
%attr(755, root, root) %{_bindir}/apcaccess
%attr(755, root, bin)  %config %{_sbindir}/powersc
%config(noreplace) /etc/apcupsd.conf
%config /etc/rc.d/init.d/apcupsd
%ghost /var/log/apcupsd.log
%ghost /etc/apcupsd.status
