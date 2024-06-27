## Pull in upstream source:
# {{{ git submodule update --init --recursive 1>&2; git submodule }}}
# {{{ git -C source tag -f 1.24.5-dev 1216ed318bb3a6e988154e4d534614ac4a4a97d2 }}}
%global gitversion		{{{ git -C source rev-parse HEAD }}}
%global gitshortversion		{{{ git -C source rev-parse --short HEAD }}}
%global gitdescribefedversion	{{{ git -C source describe --tags | sed -e 's/^\(.*\)-\([0-9]*\)-g\(.*\)$/\1^\2.g\3/' -e 's/-\([a-z]\+\)/~\1/' }}}
%global gitdescribepepversion	{{{ git -C source describe --tags | sed -e 's/-rc\([0-9]*-\)/rc\1dev-/g' -e 's/^\(.*\)-\([0-9]*\)-g\(.*\)$/\1\2/' -e 's/-/./g' }}}

Name:		mupdf
%global libname libmupdf
%global pypiname mupdf
Version:	%{gitdescribefedversion}
# git dev breaks abi without bumping!
%global soname 24.5
# upstream prerelease versions tags need to be translated to Fedorian
%global upversion %{version}
Release:	1%{?dist}
Summary:	A lightweight PDF viewer and toolkit
License:	AGPL-3.0-or-later
URL:		http://mupdf.com/
# rpkg's git_pack does not cope well with submodules, so we force it to assume a dirty tree.
# The tree is unmodified (before possibly applying patches).
Source0:	{{{ GIT_DIRTY=1 git_pack path=source dir_name=mupdf }}}
Source1:	{{{ GIT_DIRTY=1 git_pack path=source/thirdparty/extract dir_name=thirdparty/extract source_name=extract.tar.gz }}}
Source2:	{{{ GIT_DIRTY=1 git_pack path=source/thirdparty/lcms2 dir_name=thirdparty/lcms2 source_name=lcms2.tar.gz }}}
Source3:	{{{ GIT_DIRTY=1 git_pack path=source/thirdparty/mujs dir_name=thirdparty/mujs source_name=mujs.tar.gz }}}
Source11:	%{name}.desktop
Source12:	%{name}-gl.desktop
# Fedora specific patches:
# Do not bug me if Artifex relies on local fork
Patch:		0001-Do-not-complain-to-your-friendly-local-distribution-.patch
BuildRequires:	gcc gcc-c++ make binutils desktop-file-utils coreutils pkgconfig
BuildRequires:	openjpeg2-devel desktop-file-utils
BuildRequires:	libjpeg-devel freetype-devel libXext-devel curl-devel
BuildRequires:	harfbuzz-devel openssl-devel mesa-libEGL-devel
BuildRequires:	mesa-libGL-devel mesa-libGLU-devel libXi-devel libXrandr-devel
BuildRequires:	gumbo-parser-devel leptonica-devel tesseract-devel
BuildRequires:	freeglut-devel
BuildRequires:	jbig2dec-devel
BuildRequires:	swig python3-clang python3-devel
# We need to build against the Artifex fork of lcms2 so that we are thread safe
# (see bug #1553915). Artifex make sure to rebase against upstream, who refuse
# to integrate Artifex's changes. 
Provides:	bundled(lcms2-devel) = {{{ git -C source/thirdparty/lcms2 describe --tags | sed -e 's/^\(.*\)-\([0-9]*\)-g\(.*\)$/\1^\2.g\3/' -e ''s/rc/~rc/ }}}
# muPDF needs the muJS sources for the build even if we build against the system
# version so bundling them is the safer choice.
Provides:	bundled(mujs-devel) = {{{ git -C source/thirdparty/mujs describe --tags | sed -e 's/^\(.*\)-\([0-9]*\)-g\(.*\)$/\1^\2.g\3/' }}}
# muPDF builds only against in-tree extract which is versioned along with ghostpdl.
Provides:	bundled(extract) = {{{ git -C source/thirdparty/extract describe --tags | sed -e 's/^\(.*\)-\([0-9]*\)-g\(.*\)$/\1^\2.g\3/' }}}

%description
MuPDF is a lightweight PDF viewer and toolkit written in portable C.
The renderer in MuPDF is tailored for high quality anti-aliased
graphics. MuPDF renders text with metrics and spacing accurate to
within fractions of a pixel for the highest fidelity in reproducing
the look of a printed page on screen.
MuPDF has a small footprint. A binary that includes the standard
Roman fonts is only one megabyte. A build with full CJK support
(including an Asian font) is approximately seven megabytes.
MuPDF has support for all non-interactive PDF 1.7 features, and the
toolkit provides a simple API for accessing the internal structures of
the PDF document. Example code for navigating interactive links and
bookmarks, encrypting PDF files, extracting fonts, images, and
searchable text, and rendering pages to image files is provided.

%package devel
Summary:	C Development files for %{name}
Requires:	%{name}-libs%{_isa} = %{version}-%{release}

%description devel
The mupdf-devel package contains library and header files for developing
C applications that use the mupdf library.

%package libs
Summary:	C Library files for %{name}

%description libs
The mupdf-libs package contains the mupdf C library files.

%package cpp-devel
Summary:	C++ Development files for %{name}
Requires:	%{name}-cpp-libs%{_isa} = %{version}-%{release}

%description cpp-devel
The mupdf-cpp-devel package contains library and header files for developing
C++ applications that use the mupdf library.

%package cpp-libs
Summary:	C++ Library files for %{name}

%description cpp-libs
The mupdf-cpp-libs package contains the mupdf C++ library files.

%package -n python3-%{pypiname}
Summary:	Python bindings for %{name}

%description -n python3-%{pypiname}
The python3-%{pypiname} package contains low level mupdf python bindings.

%prep
%setup -a 1 -a 2 -a 3 -n mupdf
%autopatch -p1
for d in $(ls thirdparty | grep -v -e extract -e lcms2 -e mujs)
do
	rm -rf thirdparty/$d
done

echo > user.make "\
	USE_SYSTEM_LIBS := yes
	USE_SYSTEM_MUJS := no # build needs source anyways
	USE_TESSERACT := yes
	VENV_FLAG :=
	build := debug
	shared := yes
	verbose := yes
"

# c++ and python install targets rebuild unconditionally. Avoid multiple rebuilds:
sed -i -e '/^install-shared-c++:/s/ c++//' Makefile
sed -i -e '/^install-shared-python:/s/ python//' Makefile

%build
export XCFLAGS="%{optflags} -fPIC -DJBIG_NO_MEMENTO -DTOFU -DTOFU_CJK_EXT"
make %{?_smp_mflags} c++ python

%install
make DESTDIR=%{buildroot} install install-shared-c install-shared-c++ install-shared-python prefix=%{_prefix} libdir=%{_libdir} pydir=%{python3_sitearch} SO_INSTALL_MODE=755
# wheel bundles too much, so build & install with make and generate metadata here:
MUPDF_SETUP_VERSION=%{gitdescribepepversion} %{__python3} setup.py dist_info
mkdir -p %{buildroot}/%{python3_sitearch}/%{pypiname}-%{gitdescribepepversion}.dist-info
install -p -m644 mupdf-*.dist-info/METADATA/PKG-INFO %{buildroot}/%{python3_sitearch}/%{pypiname}-%{gitdescribepepversion}.dist-info/METADATA
# handle docs on our own
rm -rf %{buildroot}/%{_docdir}
desktop-file-install --dir=%{buildroot}%{_datadir}/applications %{SOURCE11}
desktop-file-install --dir=%{buildroot}%{_datadir}/applications %{SOURCE12}
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/scalable/apps
install -p -m644 docs/logo/mupdf-logo.svg %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/mupdf.svg
install -p -m644 docs/logo/mupdf-logo.svg %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/mupdf-gl.svg
find %{buildroot}/%{_mandir} -type f -exec chmod 0644 {} \;
find %{buildroot}/%{_includedir} -type f -exec chmod 0644 {} \;
cd %{buildroot}/%{_bindir} && ln -s %{name}-x11 %{name}

%files
%license COPYING
%doc README CHANGES docs/*
%{_bindir}/*
%{_datadir}/applications/mupdf*.desktop
%{_datadir}/icons/hicolor/*/apps/*
%{_mandir}/man1/*.1.gz

%files devel
%{_includedir}/%{name}
%{_libdir}/%{libname}.so

%files libs
%license COPYING
%{_libdir}/%{libname}.so.%{soname}

%files cpp-devel
%{_includedir}/%{name}
%{_libdir}/%{libname}cpp.so

%files cpp-libs
%license COPYING
%{_libdir}/%{libname}cpp.so.%{soname}

%files -n python3-%{pypiname}
%license COPYING
%{python3_sitearch}/%{pypiname}/
%{python3_sitearch}/%{pypiname}-%{gitdescribepepversion}.dist-info/

%changelog
* Fri Mar 24 2023 Michael J Gruber <mjg@fedoraproject.org> - 1.21.1^8.g861b52d57
- build from git/copr

