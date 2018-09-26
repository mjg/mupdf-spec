Name:           mupdf
Version:        1.14.0rc1
%global origversion 1.14.0-rc1
Release:        1%{?dist}
Summary:        A lightweight PDF viewer and toolkit
Group:          Applications/Publishing
License:        AGPLv3+
URL:            http://mupdf.com/
Source0:        http://mupdf.com/downloads/archive/%{name}-%{origversion}-source.tar.gz
Source1:        %{name}.desktop
BuildRequires:  gcc make binutils desktop-file-utils coreutils pkgconfig
BuildRequires:  openjpeg2-devel jbig2dec-devel desktop-file-utils
BuildRequires:  libjpeg-devel freetype-devel libXext-devel curl-devel
BuildRequires:  harfbuzz-devel
BuildRequires:  mesa-libGL-devel mesa-libGLU-devel libXi-devel libXrandr-devel
# We need to build against the Artifex fork of lcms2 so that we are thread safe
# (see bug #1553915). Artifex make sure to rebase against upstream, who refuse
# to integrate Artifex's changes. 
Provides:       bundled(lcms2-devel) = 2.9
# We need to build against the Artifex fork of freeglut so that we are unicode safe.
Provides:       bundled(freeglut-devel) = 3.0.0
# muPDF needs the muJS sources for the build even if we build against the system
# version so bundling them is the safer choice.
Provides:       bundled(mujs-devel) = 1.0.5
Patch0:         0001-fix-build-on-big-endian.patch

%description
MuPDF is a lightweight PDF viewer and toolkit written in portable C.
The renderer in MuPDF is tailored for high quality anti-aliased
graphics.  MuPDF renders text with metrics and spacing accurate to
within fractions of a pixel for the highest fidelity in reproducing
the look of a printed page on screen.
MuPDF has a small footprint.  A binary that includes the standard
Roman fonts is only one megabyte.  A build with full CJK support
(including an Asian font) is approximately five megabytes.
MuPDF has support for all non-interactive PDF 1.7 features, and the
toolkit provides a simple API for accessing the internal structures of
the PDF document.  Example code for navigating interactive links and
bookmarks, encrypting PDF files, extracting fonts, images, and
searchable text, and rendering pages to image files is provided.

%package devel
Summary:        Development files for %{name}
Group:            Development/Libraries
Requires:         %{name} = %{version}-%{release}
Provides:         %{name}-static = %{version}-%{release}

%description devel
The mupdf-devel package contains header files for developing
applications that use mupdf and static libraries

%prep
%setup -q -n %{name}-%{origversion}-source
for d in $(ls thirdparty | grep -v -e freeglut -e lcms2 -e mujs)
do
  rm -rf thirdparty/$d
done
%patch0 -p1 -d thirdparty/lcms2
echo > user.make "\
  USE_SYSTEM_FREETYPE := yes
  USE_SYSTEM_HARFBUZZ := yes
  USE_SYSTEM_JBIG2DEC := yes
  USE_SYSTEM_JPEGXR := yes # not used without HAVE_JPEGXR
  USE_SYSTEM_LCMS2 := no # need lcms2-art fork
  USE_SYSTEM_LIBJPEG := yes
  USE_SYSTEM_MUJS := no # build needs source anyways
  USE_SYSTEM_OPENJPEG := yes
  USE_SYSTEM_ZLIB := yes
  USE_SYSTEM_GLUT := no # need freeglut2-art frok
  USE_SYSTEM_CURL := yes
"

%build
export XCFLAGS="%{optflags} -fPIC -DJBIG_NO_MEMENTO -DTOFU -DTOFU_CJK"

make  %{?_smp_mflags}  build=debug verbose=yes
%install
make DESTDIR=%{buildroot} install prefix=%{_prefix} libdir=%{_libdir} build=debug verbose=yes HAVE_GLUT=yes
## handle docs on our own
rm -rf %{buildroot}/%{_docdir}
desktop-file-install --dir=%{buildroot}%{_datadir}/applications %{SOURCE1}
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/scalable/apps
install -p -m644 docs/logo/mupdf-logo.svg %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/mupdf.svg
## fix strange permissons
chmod 0644 %{buildroot}%{_libdir}/*.a
find %{buildroot}/%{_mandir} -type f -exec chmod 0644 {} \;
find %{buildroot}/%{_includedir} -type f -exec chmod 0644 {} \;
cd %{buildroot}/%{_bindir} && ln -s %{name}-x11 %{name}


%post
update-desktop-database &> /dev/null || :

%postun
update-desktop-database &> /dev/null || :

%files
%license COPYING
%doc README CHANGES docs/*
%{_bindir}/*
%{_datadir}/applications/mupdf.desktop
%{_datadir}/icons/hicolor/*/apps/*
%{_mandir}/man1/*.1.gz

%files devel
%{_includedir}/%{name}
%{_libdir}/lib%{name}*.a

%changelog
* Wed Sep 26 2018 Michael J Gruber <mjg@fedoraproject.org> - 1.14rc1-1
- rc test
- adjust to new build system setup

* Fri Jul 13 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.13.0-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Sun Jun 10 2018 Michael J Gruber <mjg@fedoraproject.org> - 1.13.0-8
- CVE-2018-10289 (rh bz #1573050) (gs bz #699271)

* Wed Jun 06 2018 Michael J Gruber <mjg@fedoraproject.org> - 1.13.0-7
- fix license field (bug #1586328)

* Sun Jun 03 2018 Michael J Gruber <mjg@fedoraproject.org> - 1.13.0-6
- fix lcms2art build on big endian

* Fri May 18 2018 Michael J Gruber <mjg@fedoraproject.org> - 1.13.0-5
- fix BR (pulled in by freeglut-devel before)

* Mon Apr 23 2018 Michael J Gruber <mjg@fedoraproject.org> - 1.13.0-4
- bundle unicode safe freeglut

* Mon Apr 23 2018 Michael J Gruber <mjg@fedoraproject.org> - 1.13.0-3
- include (now non-empty) libmupdfthird.a again (fixes bug #1553915 for zathura-pdf-mupdf)

* Fri Apr 20 2018 Michael J Gruber <mjg@fedoraproject.org> - 1.13.0-2
- bundle thread-safe lcms2 (fixes bug #1553915)

* Fri Apr 20 2018 Michael J Gruber <mjg@fedoraproject.org> - 1.13.0-1
- rebase to 1.13.0 (rh bz #1569993)

* Fri Apr 13 2018 Michael J Gruber <mjg@fedoraproject.org> - 1.12.0-6
- install svg icon

* Fri Apr 13 2018 Michael J Gruber <mjg@fedoraproject.org> - 1.12.0-6
- install svg icon

* Wed Feb 14 2018 Michael J Gruber <mjg@fedoraproject.org> - 1.12.0-5
- CVE-2018-6192 (rh bz #1539845 #1539846) (gs bz #698916)
- CVE-2018-6544 (rh bz #1542264 #1542265) (gs bz #698830 #698965)
- CVE-2018-1000051 (rh bz #1544847 #1544848) (gs bz #698825 #698873)

* Thu Feb 08 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.12.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Tue Feb 06 2018 Michael J Gruber <mjg@fedoraproject.org> - 1.12.0-4
- CVE-2018-6187 (rh bz #1538432 #1538433) (gs bz #698908)

* Wed Jan 24 2018 Michael J Gruber <mjg@fedoraproject.org> - 1.12.0-2
- CVE-2017-17858 (rh bz #1537952) (gs bz #698819)
- CVE-2018-5686 (gs bz #698860)

* Thu Dec 14 2017 Michael J Gruber <mjg@fedoraproject.org> - 1.12.0-1
- rebase to 1.12
- follow switch from GLFW to GLUT
- follow switch to new version scheme

* Sun Nov 26 2017 Michael J Gruber <mjg@fedoraproject.org> - 1.12rc1-1
- rc test

* Sat Nov 11 2017 Michael J Gruber <mjg@fedoraproject.org> - 1.11-9
- CVE-2017-15369
- CVE-2017-15587

* Sat Nov 11 2017 Michael J Gruber <mjg@fedoraproject.org> - 1.11-8
- repair FTBFS from version specific patch in 412e729 ("New release 1.11", 2017-04-11)

* Sat Nov 11 2017 Michael J Gruber <mjg@fedoraproject.org> - 1.11-7
- rebuild with jbig2dec 0.14 (#1456731)

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.11-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.11-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Tue May 09 2017 Pavel Zhukov <landgraf@fedoraproject.org> - 1.11-4
- Rebuild with new jbig2dec (#1443933)

* Fri Apr 14 2017 Pavel Zhukov <landgraf@fedoraproject.org> - 1.11-3
- Fix mupdf-gl build (#1442384)

* Tue Apr 11 2017 Pavel Zhukov <landgraf@fedoraproject.org> - 1.11-1
- New release 1.11 (#1441186)

* Thu Apr  6 2017 Pavel Zhukov <landgraf@fedoraproject.org> - 1.10a-5
- Fix stack consumption CVE (#1439643)

* Thu Mar  2 2017 Pavel Zhukov <landgraf@fedoraproject.org> - 1.10a-4
- fix buffer overflow (#1425338)

* Thu Mar 02 2017 Michael J Gruber <mjg@fedoraproject.org> - 1.10a-3
- Several packaging fixes

* Thu Feb 23 2017 Pavel Zhukov <landgraf@fedoraproject.org> - 1.10a-2
- Add comment with explanation of disabled debuginfo
- Fix make verbose output

* Sat Feb 11 2017 Pavel Zhukov <pzhukov@redhat.com> - 1.10a-1
- New release (1.10a)

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.8-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1.8-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Sat Nov 28 2015 Pavel Zhukov <landgraf@fedoraproject.org> -1.8-1
- New release (#1280518)

* Sat Nov 28 2015 Pavel Zhukov <landgraf@fedoraproject.org> -1.7a-4
- Disable memento

* Wed Nov 18 2015 Petr Šabata <contyk@redhat.com> - 1.7a-3
- Package the license text with the %%license macro
- Don't use the %%version macro in filenames, it's not helpful
- Added extra handling for the docs; %%_docdir is no longer autopackaged,
  plus we want to install the license text elsewhere

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.7a-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Mon Jun 01 2015  Pavel Zhukov <landgraf@fedoraproject.org> - 1.7a-1
- New release 1.7a (#1219482)
* Wed May 06 2015  Pavel Zhukov <landgraf@fedoraproject.org> - 1.7-1
- New release 1.7 (#1210318)
- Fix segfault in obj_close routine (#1202137, #1215752)

* Wed May 06 2015 Pavel Zhukov <landgraf@fedoraproject.org> - 1.5-6
- Fix executable name in desktop file

* Sat Oct 11 2014 Pavel Zhukov <landgraf@fedoraproject.org> - 1.5-5
- Add missed curl-devel

* Fri Jul 04 2014 Pavel Zhukov <landgraf@fedoraproject.org> - 1.5-3
- Add fPIC flag (#1109589)
- Add curl-devel to BR (#1114566)

* Sun Jun 15 2014 Pavel Zhukov <landgraf@fedoraproject.org> - 1.5-2
- Add fix for new openjpeg2

* Sun Jun 15 2014 Pavel Zhukov <landgraf@fedoraproject.org> - 1.5-1
- New release 1.5 (#1108710)

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Tue May  6 2014 Pavel Zhukov <landgraf@fedoraproject.org> - 1.4-1
- New release 1.4 (#1087287)

* Fri Jan 24 2014 Pavel Zhukov <landgraf@fedoraproject.org> - 1.1-5
- Fix stack overflow (#1056699)

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Mon Jan 21 2013 Adam Tkac <atkac redhat com> - 1.1-2
- rebuild due to "jpeg8-ABI" feature drop

* Wed Jan 09 2013 Pavel Zhukov <landgraf@fedoraproject.org> - 1.1-1
- New release

* Sun May 20 2012  Pavel Zhukov <landgraf@fedoraproject.org> - 1.0-1
- New release

* Wed Mar 14 2012  Pavel Zhukov <landgraf@fedoraproject.org> - 0.9-2
- Fix buffer overflow (#752388)

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.9-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild
