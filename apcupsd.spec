Name:		apcupsd
Version:	3.5.8
Release:	2
License:	GPL v2
Group:		System Environment/Daemons
Source:		http://www.brisse.dk/site/apcupsd/download/%{name}-%{version}.src.tar.gz
Patch0:		apcups-initscript.patch
Patch1:		apcups-makefile.patch
Summary:	power management software for APC UPS hardware
URL:		http://www.brisse.dk/site/apcupsd/
BuildRoot:	/tmp/%{name}-%{version}-root
#Icon:		apcupsd-logo.xpm

%description
UPS power management under Linux for APCC Products. It allows your
computer/server to run during power problems for a specified length of time
or the life of the batteries in your BackUPS, BackUPS Pro, SmartUPS v/s, or
SmartUPS, and then properly executes a controlled shutdown during an
extended power failure.

%prep
%setup -q -n %{name}-%{version}.src
%patch0 -p1
%patch1 -p1

%build
mv Makefile Makefile.orig
cat Makefile.orig \
 | sed "s,^PREFIX    =,PREFIX    = ${RPM_BUILD_ROOT},"  \
 | sed "s,^MANPREFIX = /usr,MANPREFIX = ${RPM_BUILD_ROOT}/usr," \
 > Makefile
make linux

%install
rm -rf ${RPM_BUILD_ROOT}

# Some issues :
# - why doesn't the Makefile know that it should install *-linux ??
# - make install tries to stop apcupsd. That's not necessary (buildroot) (hany: not issue anymore)

install -d ${RPM_BUILD_ROOT}/{sbin,bin,etc/rc.d/init.d,usr/man/man8,var/log}
NAME="-linux" make install
# hany: why this? we're just building. not installing
#[ -x /sbin/powersc ] && /sbin/powersc RESTARTME
gzip -9nf  ${RPM_BUILD_ROOT}/usr/man/*/*.?
cp -f installs/apcupsd.conf ${RPM_BUILD_ROOT}/etc
cp -f installs/apcups.rhs ${RPM_BUILD_ROOT}/etc/rc.d/init.d/apcups
touch ${RPM_BUILD_ROOT}/var/log/apcupsd.log
touch ${RPM_BUILD_ROOT}/etc/apcupsd.status

%clean
rm -rf ${RPM_BUILD_ROOT}

%post
/sbin/ldconfig
/sbin/chkconfig --add apcups
if !(grep /sbin/powersc /etc/rc.d/init.d/halt > /dev/null); then
cp -f /etc/rc.d/init.d/halt /etc/rc.d/init.d/halt.rpmorig
sed -e '/# Now halt or reboot./i\' \
     -e '\
# See if this is a powerfail situation.\
if [ -f /etc/powerfail ]; then\
  echo "APCUPSD to the Rescue!"\
  echo\
  /sbin/powersc KILL\
  echo\
  sleep 120\
  exit 1\
fi\
' /etc/rc.d/init.d/halt.rpmorig > /etc/rc.d/init.d/halt

fi
echo Check the documentation to see whether /etc/rc.d/init.d/halt has a
echo correct invocation of /sbin/powersc .

%preun
chkconfig --del apcups

%files
%defattr(644,root,root,755)
%attr(-, root, root) %doc README.NEW Changelog port.gif Statement.APCC
%attr(-, root, root) %doc %{name}-%{version}.src.lsm
%attr(-, root, root) %doc readmes/*
%attr(-, root, root) %doc docs/apcupsd.docs
%attr(-, root, root) %doc installs/halt.rhs installs/apcups.rhs installs/powersc
/usr/man/man8/apcupsd.8.gz
%attr(755, root, bin)  /sbin/apcupsd
%attr(755, root, root) /bin/apcaccess
%attr(755, root, bin)  %config /sbin/powersc
%attr(640, root, root) %config(noreplace) /etc/apcupsd.conf
%attr(754, root, root) /etc/rc.d/init.d/apcups
%ghost /var/log/apcupsd.log
%ghost /etc/apcupsd.status
