Name: apcupsd
Version: 3.5.8
Release: 2
Copyright: GPL v2
Group: System Environment/Daemons
Url: http://www.brisse.dk/site/apcupsd/
Packager: Bert de Bruijn <bob@ccl.kuleuven.ac.be>
Source: http://www.brisse.dk/site/apcupsd/download/%{name}-%{version}.src.tar.gz
Patch0: apcups-initscript.patch
Patch1: apcups-makefile.patch
Summary: power management software for APC UPS hardware
BuildRoot: /var/tmp/%{name}-root
Prefix: /usr
Prefix: /etc
Prefix: /sbin
Prefix: /bin
Prefix: /var
#Icon: apcupsd-logo.xpm

%description
UPS power management under Linux for APCC Products.
It allows your computer/server to run during power problems
for a specified length of time or the life of the batteries
in your BackUPS, BackUPS Pro, SmartUPS v/s, or SmartUPS, and
then properly executes a controlled shutdown during an
extended power failure.

%prep
%setup -n %{name}-%{version}.src
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
# Some issues :
# - why doesn't the Makefile know that it should install *-linux ??
# - make install tries to stop apcupsd. That's not necessary (buildroot) (hany: not issue anymore)

mkdir -p ${RPM_BUILD_ROOT}/{sbin,bin,etc/rc.d/init.d,usr/man/man8,var/log}
NAME="-linux" make install
# hany: why this? we're just building. not installing
#[ -x /sbin/powersc ] && /sbin/powersc RESTARTME
gzip -9 -f ${RPM_BUILD_ROOT}/usr/man/*/*.?
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
%defattr(-, root, root)
%attr(-, root, root) %doc README.NEW Changelog port.gif Statement.APCC
%attr(-, root, root) %doc %{name}-%{version}.src.lsm
%attr(-, root, root) %doc readmes/*
%attr(-, root, root) %doc docs/apcupsd.docs
%attr(-, root, root) %doc installs/halt.rhs installs/apcups.rhs installs/powersc
%attr(644, root, man) /usr/man/man8/apcupsd.8.gz
%attr(755, root, bin)  /sbin/apcupsd
%attr(755, root, root) /bin/apcaccess
%attr(755, root, bin)  %config /sbin/powersc
%attr(640, root, root) %config(noreplace) /etc/apcupsd.conf
%attr(755, root, root) %config /etc/rc.d/init.d/apcups
%ghost /var/log/apcupsd.log
%ghost /etc/apcupsd.status

%changelog
* Fri Aug  6 1999 Peter Hanecak <hanecak@megaloman.sk>
- build process cleaned (so non-root users can do that smoothly)
- build-root changed
- %defattr

* Sun Jun  6 1999 Bert de Bruijn <bob@ccl.kuleuven.ac.be>
- new spec file, first rpm release since source release under GPL ?
- use sed in %build to force buildroot.
