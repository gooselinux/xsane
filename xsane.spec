# if you rebuild, please change bugtracker_url accordingly:
%global bugtracker_url http://bugzilla.redhat.com

%global gimpplugindir %(gimptool --gimpplugindir)/plug-ins

# work around old %%configure macro
%if ! (0%{?rhel} > 6 || 0%{?fedora} > 12)
%global configure %(echo '%configure' | sed 's+\./configure+%%{_configure}+g')
%endif

# needed for off-root building
%global _configure ../configure

Name: xsane
Summary: X Window System front-end for the SANE scanner interface
Version: 0.997
Release: 8%{?dist}
Source0: http://www.xsane.org/download/%{name}-%{version}.tar.gz
Source1: xsane.desktop
# distro-specific: use "xdg-open" instead of "netscape" to launch help browser
Patch0: xsane-0.995-xdg-open.patch
# submitted to upstream (Oliver Rauch) via email, 2009-08-18
Patch1: xsane-0.995-close-fds.patch
# https://bugzilla.redhat.com/show_bug.cgi?id=504344
# distro-specific, upstream won't accept it: "don't show license dialog"
Patch2: xsane-0.996-no-eula.patch
# enable off-root building
# submitted to upstream (Oliver Rauch) via email, 2010-06-23
Patch3: xsane-0.997-off-root-build.patch
# https://bugzilla.redhat.com/show_bug.cgi?id=608047
# submitted to upstream (Oliver Rauch) via email, 2010-06-28
Patch4: xsane-0.997-no-file-selected.patch
# https://bugzilla.redhat.com/show_bug.cgi?id=198422
# submitted to upstream (Oliver Rauch) via email, 2010-06-29
Patch5: xsane-0.997-ipv6.patch
# autoconf-generated files
Patch10: xsane-0.997-5-autoconf.patch.bz2
License: GPLv2+
URL: http://www.xsane.org/
Group: Applications/Multimedia
Buildroot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%__id_u -n)
BuildRequires: gimp-devel
BuildRequires: lcms-devel
BuildRequires: libjpeg-devel
BuildRequires: libpng-devel
BuildRequires: sane-backends-devel >= 1.0.19-15
BuildRequires: desktop-file-utils >= 0.2.92
BuildRequires: libtiff-devel
BuildRequires: gettext-devel
Requires: xsane-common

%description
XSane is an X based interface for the SANE (Scanner Access Now Easy)
library, which provides access to scanners, digital cameras, and other
capture devices. XSane is written in GTK+ and provides control for
performing the scan and then manipulating the captured image.

%package gimp
Summary: GIMP plug-in providing the SANE scanner interface
Group: Applications/Multimedia
Requires: gimp >= 2:2.2.12-4
Requires: xsane-common

%description gimp
This package provides the regular XSane frontend for the SANE scanner
interface, but it works as a GIMP plug-in. You must have GIMP
installed to use this package.

%package common
Summary: Common files for xsane packages
Group: Applications/Multimedia

%description common
This package contains common files needed by other xsane packages.

%prep
%setup -q

# convert some files to UTF-8
for doc in xsane.{CHANGES,PROBLEMS,INSTALL}; do
    iconv -f ISO-8859-1 -t utf8 "$doc" -o "$doc.new" && \
    touch -r "$doc" "$doc.new" && \
    mv "$doc.new" "$doc"
done

%patch0 -p1 -b .xdg-open
%patch1 -p1 -b .close-fds
%patch2 -p1 -b .no-eula
%patch3 -p1 -b .off-root-build
%patch4 -p1 -b .no-file-selected
%patch5 -p1 -b .ipv6

%patch10 -p1 -b .autoconf

# in-root config.h breaks off-root building
rm include/config.h

mkdir build-with-gimp
mkdir build-without-gimp

%build
CC='gcc -DXSANE_BUGTRACKER_URL=\"%{bugtracker_url}\"'
export CC

pushd build-with-gimp
%configure --enable-gimp
make %{?_smp_mflags}
popd

pushd build-without-gimp
%configure --disable-gimp
make
popd

%install
rm -rf %{buildroot}

pushd build-without-gimp
make DESTDIR=%{buildroot} install
popd

# install GIMP plugin
install -m 0755 -d %{buildroot}%{gimpplugindir}
install -m 0755 build-with-gimp/src/xsane %{buildroot}%{gimpplugindir}

# use our own desktop file
rm %{buildroot}%{_datadir}/applications/xsane.desktop
desktop-file-install --vendor fedora \
    --dir %{buildroot}%{_datadir}/applications \
    %{SOURCE1}

%find_lang %{name} XSANE.lang

%clean
rm -rf %{buildroot}

%pre gimp
# remove obsolete gimp-plugin-mgr managed symlink
if [ -L "%{gimpplugindir}/xsane" ]; then
    rm -f "%{gimpplugindir}/xsane"
fi

%files -f XSANE.lang
%defattr(-,root,root)
%doc xsane.ACCELKEYS xsane.AUTHOR xsane.BEGINNERS-INFO xsane.BUGS xsane.CHANGES xsane.COPYING xsane.FAQ xsane.LANGUAGES xsane.LOGO xsane.NEWS xsane.ONLINEHELP xsane.PROBLEMS xsane.ROOT xsane.TODO
%{_bindir}/xsane
%{_mandir}/man1/*
%{_datadir}/applications/fedora-xsane.desktop
%{_datadir}/pixmaps/xsane.xpm

%files gimp
%defattr(-,root,root)
%{gimpplugindir}/xsane

%files common
%defattr(-,root,root)
%dir %{_datadir}/sane
%{_datadir}/sane/xsane

%changelog
* Tue Jun 29 2010 Nils Philippsen <nils@redhat.com> 0.997-8
- support IPv6 (#198422)

* Mon Jun 28 2010 Nils Philippsen <nils@redhat.com> 0.997-7
- work around old %%configure macro

* Mon Jun 28 2010 Nils Philippsen <nils@redhat.com> 0.997-6
- don't crash if no files are selected (#608047)

* Wed Jun 23 2010 Nils Philippsen <nils@redhat.com> 0.997-5
- don't use gimp-plugin-mgr anymore
- use off-root builds

* Thu Feb 25 2010 Nils Philippsen <nils@redhat.com> 0.997-4
- quote RPM macros in changelog

* Tue Aug 18 2009 Nils Philippsen <nils@redhat.com>
- explain patches

* Wed Aug 05 2009 Nils Philippsen <nils@redhat.com> 0.997-3
- Merge Review (#226658):
  - replace %%desktop_vendor macro with "fedora"
  - fix xsane-gimp requirements
  - move EULA and documentation into -common subpackage

* Mon Aug 03 2009 Nils Philippsen <nils@redhat.com> 0.997-2
- remove ExcludeArch: s390 s390x

* Fri Jul 31 2009 Nils Philippsen <nils@redhat.com> 0.997-1
- version 0.997
- drop obsolete sane-backends-1.0.20 patch

* Mon Jul 27 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.996-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Tue Jul 21 2009 Nils Philippsen <nils@redhat.com> 0.996-9
- don't show EULA, mention bugzilla in about dialog (#504344)

* Mon Jul 20 2009 Nils Philippsen <nils@redhat.com> 0.996-8
- don't use obsolete SANE_CAP_ALWAYS_SETTABLE macro (#507823)

* Tue Jul  7 2009 Tom "spot" Callaway <tcallawa@redhat.com> 0.996-7
- don't own %%{_datadir}/applications/ (filesystem package owns it)

* Fri May 29 2009 Nils Philippsen <nils@redhat.com>
- Merge review (#226658):
  - convert documentation files to UTF-8
  - don't BR: sed
  - don't own %%{_datadir}/applications, %%{_sysconfdir}/gimp,
    %%{_sysconfdir}/gimp/plugins.d
  - don't package unnecessary documentation

* Mon Mar 02 2009 Nils Philippsen <nils@redhat.com> - 0.996-6
- rebuild against new sane-backends (just in case)

* Thu Feb 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.996-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Tue Jan 20 2009 Nils Philippsen <nphilipp@redhat.com> - 0.996-3
- pickup changed desktop file, close-fds patch in F9, F10

* Tue Jan 20 2009 Nils Philippsen <nphilipp@redhat.com> - 0.996-2
- BR: lcms-devel

* Sun Jan 18 2009 Nils Philippsen <nphilipp@redhat.com> - 0.996-1
- version 0.996
- don't use %%makeinstall
- use shipped xsane.xpm as application icon

* Fri Jul 18 2008 Nils Philippsen <nphilipp@redhat.com> - 0.995-5
- fix fd leak prevention (#455450)

* Tue Jul 15 2008 Nils Philippsen <nphilipp@redhat.com> - 0.995-4
- don't leak file descriptors to help browser process (#455450)

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 0.995-3
- Autorebuild for GCC 4.3

* Thu Nov 29 2007 Nils Philippsen <nphilipp@redhat.com> - 0.995-2
- make EULA, license dialogs be viewable on 800x600 displays

* Fri Nov 23 2007 Nils Philippsen <nphilipp@redhat.com> - 0.995-1
- version 0.995
- remove obsolete gimp2.0, medium-definitions, showeulaonce patches

* Thu Oct 15 2007 Nils Philippsen <nphilipp@redhat.com>
- explicitely enable building the gimp plugin in configure call
- reorder spec file sections

* Wed Sep 05 2007 Nils Philippsen <nphilipp@redhat.com> - 0.994-4
- fix "Category" entries in desktop file

* Wed Sep 05 2007 Nils Philippsen <nphilipp@redhat.com>
- change license to GPLv2+

* Tue Apr 24 2007 Nils Philippsen <nphilipp@redhat.com> - 0.994-3
- don't include obsolete Application category in desktop file (#226658)

* Wed Apr 04 2007 Nils Philippsen <nphilipp@redhat.com> - 0.994-2
- save prefs when EULA is accepted to ensure that EULA is only shown once at
  startup (#233645)

* Tue Apr 03 2007 Nils Philippsen <nphilipp@redhat.com> - 0.994-1
- version 0.994 (#235038)

* Fri Mar 30 2007 Nils Philippsen <nphilipp@redhat.com> - 0.993-2
- fix summaries and buildroot, don't remove buildroot on %%prep, mark dirs and
  config files, don't reference %%buildroot in %%build, use double-%% in
  changelog entries (#226658)

* Fri Mar 02 2007 Nils Philippsen <nphilipp@redhat.com> - 0.993-1
- version 0.993 (#230706)

* Wed Oct 25 2006 Nils Philippsen <nphilipp@redhat.com> - 0.991-4
- fix typo in scriptlet (#212063)

* Mon Oct 23 2006 Nils Philippsen <nphilipp@redhat.com> - 0.991-3
- really don't barf on missing gimp-plugin-mgr when updating (#208159)

* Mon Oct 02 2006 Nils Philippsen <nphilipp@redhat.com> - 0.991-2
- don't barf on missing gimp-plugin-mgr when updating (#208159)

* Mon Aug 28 2006 Nils Philippsen <nphilipp@redhat.com> - 0.991-1
- version 0.991
- remove obsolete buffer patch

* Wed Aug 16 2006 Nils Philippsen <nphilipp@redhat.com> - 0.99-6
- revamp scheme for integrating external GIMP plugins (#202545)
- use disttag

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 0.99-5.1
- rebuild

* Thu Jun 08 2006 Nils Philippsen <nphilipp@redhat.com> - 0.99-5
- re-add desktop file (#170835)
- use %%buildroot consistently
- add automake, autoconf build requirements

* Wed Apr 05 2006 Nils Philippsen <nphilipp@redhat.com> - 0.99-4
- use XSANE.lang instead of xsane.lang to avoid %%doc multilib regression

* Tue Apr 04 2006 Nils Philippsen <nphilipp@redhat.com> - 0.99-3
- fix medium-definitions patch to not barf on obsolete options in config file
  (#185269, by Aldy Hernandez)

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 0.99-2.2
- bump again for double-long bug on ppc(64)

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 0.99-2.1
- rebuilt for new gcc4.1 snapshot and glibc changes

* Mon Jan 16 2006 Nils Philippsen <nphilipp@redhat.com> 0.99-2
- fix buffer overflow

* Fri Jan 13 2006 Nils Philippsen <nphilipp@redhat.com> 0.99-1
- version 0.99

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Thu Nov 24 2005 Nils Philippsen <nphilipp@redhat.com> 0.98a-1
- version 0.98a

* Tue Oct 04 2005 Nils Philippsen <nphilipp@redhat.com> 0.97-1
- version 0.97

* Mon Jun 20 2005 Tim Waugh <twaugh@redhat.com> 0.95-4
- Build requires gettext-devel (bug #160994).

* Wed Mar  2 2005 Tim Waugh <twaugh@redhat.com> 0.95-3
- Rebuild for new GCC.

* Wed Dec  8 2004 Tim Waugh <twaugh@redhat.com> 0.95-2
- Fix crash on start (bug #142148).

* Fri Dec  3 2004 Tim Waugh <twaugh@redhat.com> 0.95-1
- 0.95.
- No longer need badcode patch.
- Enable translations again.
- New method of installing GIMP plug-in due to Nils Philippsen.

* Mon Jun 28 2004 Tim Waugh <twaugh@redhat.com> 0.92-13
- Build requires libtiff-devel (bug #126564).

* Tue Jun 15 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Fri Jun  4 2004 Tim Waugh <twaugh@redhat.com> 0.92-11
- Fix GIMP plug-in package (bug #125254).

* Wed Apr 21 2004 Seth Nickell <snickell@redhat.com> 0.92-10
- Remove .desktop file

* Wed Mar 31 2004 Tim Waugh <twaugh@redhat.com> 0.92-9
- Rebuilt.

* Thu Mar 18 2004 Nils Philippsen <nphilipp@redhat.com> 0.92-8
- Rebuild against new gimp.

* Tue Mar  9 2004 Tim Waugh <twaugh@redhat.com> 0.92-7
- Fix desktop file Name (bug #117370).

* Fri Feb 13 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Fri Feb 13 2004 Tim Waugh <twaugh@redhat.com> 0.92-5
- Fixed %%post scriptlet.

* Sun Jan 25 2004 Tim Waugh <twaugh@redhat.com> 0.92-4
- Gimp patch updated.

* Fri Jan 23 2004 Tim Waugh <twaugh@redhat.com> 0.92-3
- Translations are broken -- turn them off for the time being.
- Really apply the patch this time.
- Fix up post/postun scriptlets.

* Fri Jan 23 2004 Tim Waugh <twaugh@redhat.com> 0.92-2
- Apply patch for building against new gimp.

* Mon Dec 15 2003 Tim Waugh <twaugh@redhat.com> 0.92-1
- 0.92.

* Thu Nov 27 2003 Thomas Woerner <twoerner@redhat.com> 0.91-2
- removed rpath

* Wed Oct  8 2003 Tim Waugh <twaugh@redhat.com>
- Avoid undefined behaviour in xsane-preview.c (bug #106314).

* Thu Jul 24 2003 Tim Waugh <twaugh@redhat.com> 0.91-1
- 0.91.

* Wed Jun 04 2003 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Wed Apr  9 2003 Tim Waugh <twaugh@redhat.com> 0.90-2
- Set default HTML viewer to htmlview (bug #88318).

* Thu Mar 20 2003 Tim Waugh <twaugh@redhat.com> 0.90-1
- 0.90.

* Sat Feb  1 2003 Matt Wilson <msw@redhat.com> 0.89-3
- use %%{_libdir} for gimp plugin path

* Wed Jan 22 2003 Tim Powers <timp@redhat.com>
- rebuilt

* Fri Oct 25 2002 Tim Waugh <twaugh@redhat.com> 0.89-1
- 0.89.
- Use %%find_lang.

* Fri Aug 30 2002 Tim Waugh <twaugh@redhat.com> 0.84-8
- Don't require gimp-devel (cf. bug #70754).

* Tue Jul 23 2002 Tim Waugh <twaugh@redhat.com> 0.84-7
- Desktop file fixes (bug #69555).

* Mon Jul 15 2002 Tim Waugh <twaugh@redhat.com> 0.84-6
- Use desktop-file-install.

* Fri Jun 21 2002 Tim Powers <timp@redhat.com> 0.84-5
- automated rebuild

* Wed Jun 12 2002 Tim Waugh <twaugh@redhat.com> 0.84-4
- Rebuild to fix bug #66132.

* Thu May 23 2002 Tim Powers <timp@redhat.com> 0.84-3
- automated rebuild

* Thu Feb 21 2002 Tim Waugh <twaugh@redhat.com> 0.84-2
- Rebuild in new environment.

* Wed Jan 23 2002 Tim Waugh <twaugh@redhat.com> 0.84-1
- 0.84.
- Remove explicit sane-backends dependency, since it is automatically
  found by rpm.

* Wed Jan 09 2002 Tim Powers <timp@redhat.com> 0.83-2
- automated rebuild

* Tue Jan  8 2002 Tim Waugh <twaugh@redhat.com> 0.83-1
- 0.83.

* Tue Dec 11 2001 Tim Waugh <twaugh@redhat.com> 0.82-3.1
- 0.82.
- Some extra patches from Oliver Rauch.
- Require sane not sane-backends since it's available throughout 7.x.
- Built for Red Hat Linux 7.1, 7.2.

* Tue Jul 24 2001 Tim Waugh <twaugh@redhat.com> 0.77-4
- Build requires libpng-devel, libjpeg-devel (#bug 49760).

* Tue Jul 17 2001 Preston Brown <pbrown@redhat.com> 0.77-3
- add an icon to the desktop entry

* Tue Jun 19 2001 Florian La Roche <Florian.LaRoche@redhat.de>
- add ExcludeArch: s390 s390x

* Mon Jun 11 2001 Tim Waugh <twaugh@redhat.com> 0.77-1
- 0.77.

* Sun Jun  3 2001 Tim Waugh <twaugh@redhat.com> 0.76-2
- Require sane-backends, not all of sane.

* Wed May 23 2001 Tim Waugh <twaugh@redhat.com> 0.76-1
- 0.76.

* Thu May  3 2001 Tim Waugh <twaugh@redhat.com> 0.75-1
- 0.75
- Fix summary/description to match specspo.

* Mon Jan  8 2001 Matt Wilson <msw@redhat.com>
- fix post script of gimp subpackage to install into the correct location

* Mon Dec 25 2000 Matt Wilson <msw@redhat.com>
- rebuilt against gimp 1.2.0

* Thu Dec 21 2000 Matt Wilson <msw@redhat.com>
- rebuilt against gimp 1.1.32
- use -DGIMP_ENABLE_COMPAT_CRUFT=1 to build with compat macros

* Thu Oct 12 2000 Than Ngo <than@redhat.com>
- 0.62

* Wed Aug 23 2000 Matt Wilson <msw@redhat.com>
- rebuilt against gimp-1.1.25

* Mon Aug 07 2000 Than Ngo <than@redhat.de>
- added swedish translation (Bug #15316)

* Fri Aug 4 2000 Than Ngo <than@redhat.de>
- fix, shows error dialogbox if no scanner exists (Bug #15445)
- update to 0.61

* Wed Aug  2 2000 Matt Wilson <msw@redhat.com>
- rebuilt against new libpng

* Thu Jul 13 2000 Prospector <bugzilla@redhat.com>
- automatic rebuild

* Mon Jul  3 2000 Matt Wilson <msw@redhat.com>
- rebuilt against gimp 1.1.24
- make clean before building non gimp version

* Fri Jun 30 2000 Preston Brown <pbrown@redhat.com>
- made gimp subpkg

* Wed Jun 14 2000 Preston Brown <pbrown@redhat.com>
- desktop entry added

* Tue Jun 13 2000 Preston Brown <pbrown@redhat.com>
- fixed gimp link
- FHS paths

* Tue May 30 2000 Karsten Hopp <karsten@redhat.de>
- update to 0.59

* Sat Jan 29 2000 TIm Powers <timp@redhat.com>
- fixed bug 8948

* Thu Dec 2 1999 Tim Powers <timp@redhat.com>
- updated to 0.47
- gzip man pages

* Mon Aug 30 1999 Tim Powers <timp@redhat.com>
- changed group

* Mon Jul 26 1999 Tim Powers <timp@redhat.com>
- update to 0.30
- added %%defattr
- built for 6.1

* Thu Apr 22 1999 Preston Brown <pbrown@redhat.com>
- initial RPM for PowerTools 6.0
