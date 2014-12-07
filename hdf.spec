%define _disable_ld_no_undefined 1

%bcond_with	gfortran
# the build requires either:
# 1.	--disable-shared --enable-gfortran
# 2.	--enable-shared --disable-gfortran
# choose wisely

%define major	0
%define libdf	%mklibname df %{major}
%define libmfhdf %mklibname mfhdf %{major}
%define devname	%mklibname %{name} -d
%define staname	%mklibname %{name} -d -s

Summary:	Hierarchical Data Format Library
Name:		hdf
Version:	4.2.10
Release:	5
License:	BSD
Group:		Development/C
Url:		http://www.hdfgroup.org/
Source0:	ftp://ftp.hdfgroup.org/HDF/HDF_Current/src/%{name}-%{version}.tar.bz2
# fedora patches
Patch0:		hdf-4.2.5-maxavailfiles.patch
Patch1:		hdf-tirpc.patch
Patch2:		hdf-4.2.6-compile.patch
Patch4: 	hdf-arm.patch
# Support DESTDIR in install-examples
Patch5: 	hdf-destdir.patch
# Install examples into the right location
Patch6:		hdf-examplesdir.patch
# Fix build with -Werror=format-security
# https://bugzilla.redhat.com/show_bug.cgi?id=1037120
Patch7:		hdf-format.patch
# since there is not support for ppc, sparc & s390
# not going to import patches

BuildRequires:	byacc
BuildRequires:	chrpath
%if %{with gfortran}
BuildRequires:	gcc-gfortran
%endif
BuildRequires:	flex
BuildRequires:	jpeg-devel
BuildRequires:	pkgconfig(netcdf)
BuildRequires:	pkgconfig(zlib)

%description
HDF is a multi-object file format that facilitates the transfer of various
types of scientific data between machines and operating systems. 
HDF allows self-definitions of data content and easy extensibility for
future enhancements or compatibility with other standard formats.
HDF includes Fortran and C calling interfaces, and utilities to
prepare raw image of data files or for use with other NCSA software.

%package util
Summary:	HDF utilities and test data files
Group:		Graphics
Provides:	HDF-util

%description util
This package contains utilities for HDF data manipulation and
test data files.

%if %{without gfortran}
%package -n %{libdf}
Summary:	Libraries for the %{name} package
Group:		System/Libraries

%description -n %{libdf}
Library for %{name}.

%package -n %{libmfhdf}
Summary:	Libraries for the %{name} package
Group:		System/Libraries

%description -n %{libmfhdf}
Library for %{name}.
%endif

%package -n %{devname}
Summary:	Development headers and development libraries
Group:		Development/Other
Requires:	%{libdf} = %{version}
Requires:	%{libmfhdf} = %{version}
Provides:	%{name}-devel = %{version}-%{release}
Provides:	%{staname} = %{version}-%{release}

%description -n %{devname}
%{name} development headers and libraries.

%prep
%setup -q
%apply_patches
autoreconf -fi
#libtoolize --force
#aclocal
#autoheader
#automake -a
#autoconf

# Make it lib64 aware
find . -name Makefile.in | \
  xargs perl -pi -e "s,^(libdir|LIBDIR)\s+=.+,\1 = \\\$(prefix)/%{_lib},"

%build
# Build with PIC in case static library is built into a DSO afterwards
%ifarch ia64 x86_64
export CFLAGS="%{optflags} -ansi -D_BSD_SOURCE -DPC -DPIC -fPIC"
%else
export CFLAGS="%{optflags} -ansi -D_BSD_SOURCE -DPC"
%endif
export CXXFLAGS=$CFLAGS
export FFLAGS="%{optflags} -ffixed-line-length-none"

%configure \
	--enable-static \
%if %{with gfortran}
	--enable-fortran \
	--disable-netcdf \
%else
	--disable-fortran \
	--enable-shared \
%endif
	--disable-production

make
%if %{with gfortran}
# correct the timestamps based on files used to generate the header files
touch -c -r hdf/src/hdf.inc hdf/src/hdf.f90
touch -c -r hdf/src/dffunc.inc hdf/src/dffunc.f90
touch -c -r mfhdf/fortran/mffunc.inc mfhdf/fortran/mffunc.f90
# netcdf fortran include need same treatement, but they are not shipped
%endif

%check
make check

%install
mkdir -p %{buildroot}%{_docdir}/%{name}/examples/c
make install DESTDIR=%{buildroot} INSTALL='install -p'

# remove files already provided by other packages (libjpeg, netcdf, zlib)
rm -f %{buildroot}%{_includedir}/{jconfig.h,jerror.h,jmorecfg.h,jpeglib.h} \
    %{buildroot}%{_includedir}/{zconf.h,zlib.h} \
    %{buildroot}%{_bindir}/{ncdump,ncgen} \
    %{buildroot}%{_includedir}/netcdf.{h,inc,f90} \
    %{buildroot}%{_mandir}/man1/ncgen.1 \
    %{buildroot}%{_mandir}/man1/ncdump.1

mv -f %{buildroot}%{_bindir}/vmake %{buildroot}%{_bindir}/vmake-hdf

# this is done to have the same timestamp on multiarch setups
touch -c -r README.txt $RPM_BUILD_ROOT/%{_includedir}/h4config.h

# Remove an autoconf conditional from the API that is unused and cause
# the API to be different on x86 and x86_64
pushd $RPM_BUILD_ROOT/%{_includedir}
grep -v 'H4_SIZEOF_INTP' h4config.h > h4config.h.tmp
touch -c -r h4config.h h4config.h.tmp
mv h4config.h.tmp h4config.h
popd

# fix rpath in binaries & libraries
chrpath -d \
%{buildroot}%{_bindir}/vshow \
%{buildroot}%{_bindir}/hdfimport \
%{buildroot}%{_bindir}/hdiff \
%{buildroot}%{_bindir}/hdfls \
%{buildroot}%{_bindir}/r8tohdf \
%{buildroot}%{_bindir}/hdfcomp \
%{buildroot}%{_bindir}/hdfunpac \
%{buildroot}%{_bindir}/gif2hdf \
%{buildroot}%{_bindir}/hdf24to8 \
%{buildroot}%{_bindir}/jpeg2hdf \
%{buildroot}%{_bindir}/hdf2jpeg \
%{buildroot}%{_bindir}/hdfed \
%{buildroot}%{_bindir}/vmake-hdf \
%{buildroot}%{_bindir}/hdp \
%{buildroot}%{_bindir}/hdftor8 \
%{buildroot}%{_bindir}/hdftopal \
%{buildroot}%{_bindir}/hdfpack \
%{buildroot}%{_bindir}/paltohdf \
%{buildroot}%{_bindir}/ristosds \
%{buildroot}%{_bindir}/hdf2gif \
%{buildroot}%{_bindir}/hrepack \
%{buildroot}%{_bindir}/hdf8to24 \
%if %{without gfortran}
%{buildroot}%{_libdir}/lib*.so.%{major}.*
%endif

%files util
%{_bindir}/*
%{_mandir}/man1/*

%if %{without gfortran}
%files -n %{libdf}
%{_libdir}/libdf.so.%{major}*

%files -n %{libmfhdf}
%{_libdir}/libmfhdf.so.%{major}*
%endif

%files -n %{devname}
%doc COPYING
%doc %{_docdir}/%{name}
%{_libdir}/lib*.a
%if %{without gfortran}
%{_libdir}/lib*.so
%endif
%{_libdir}/libhdf4.settings
%{_includedir}/*
