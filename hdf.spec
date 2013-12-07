%define _disable_ld_no_undefined 1

%define major	0
%define libdf	%mklibname df %{major}
%define libmfhdf %mklibname mfhdf %{major}
%define devname	%mklibname %{name} -d

Summary:	Hierarchical Data Format Library
Name:		hdf
Version:	4.2.6
Release:	4
License:	BSD
Group:		Development/C
Url:		http://www.hdfgroup.org/
Source0:	ftp://ftp.hdfgroup.org/HDF/HDF_Current/src/%{name}-%{version}.tar.bz2
# fedora patches
Patch0:		hdf-4.2.5-maxavailfiles.patch
Patch1:		hdf-4.2.6-tirpc.patch
Patch2:		hdf-4.2.6-compile.patch
# since there is not support for ppc, sparc & s390
# not going to import patches
# mandriva patches
Patch7:		HDF4.2r4-format_not_a_string_literal_and_no_format_arguments.diff

BuildRequires:	byacc
BuildRequires:	flex
BuildRequires:	chrpath
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

%description util
This package contains utilities for HDF data manipulation and
test data files.

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

%package -n %{devname}
Summary:	Development headers and development libraries
Group:		Development/Other
Requires:	%{libdf} = %{version}
Requires:	%{libmfhdf} = %{version}
Provides:	%{name}-devel = %{version}-%{release}

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
export FFLAGS="%{optflags}"

%configure2_5x \
	--disable-static \
	--enable-shared \
	--disable-fortran \
	--enable-production

%make

mkdir -p samples
cp -a hdf/util/testfiles/* samples

%check
make check

%install
%makeinstall_std

# remove files already provided by other packages (libjpeg, netcdf, zlib)
rm -f %{buildroot}%{_includedir}/{jconfig.h,jerror.h,jmorecfg.h,jpeglib.h} \
    %{buildroot}%{_includedir}/{zconf.h,zlib.h} \
    %{buildroot}%{_bindir}/{ncdump,ncgen} \
    %{buildroot}%{_includedir}/netcdf.{h,inc,f90} \
    %{buildroot}%{_mandir}/man1/ncgen.1 \
    %{buildroot}%{_mandir}/man1/ncdump.1

mv -f %{buildroot}%{_bindir}/vmake %{buildroot}%{_bindir}/vmake-hdf
mkdir -p %{buildroot}%{_datadir}/hdf
cp -aR samples %{buildroot}%{_datadir}/hdf/

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
%{buildroot}%{_libdir}/lib*.so.%{major}.*

%files util
%{_bindir}/*
%{_mandir}/man1/*

%files -n %{libdf}
%{_libdir}/libdf.so.%{major}*

%files -n %{libmfhdf}
%{_libdir}/libmfhdf.so.%{major}*

%files -n %{devname}
%doc COPYING
%{_libdir}/lib*.so
%{_libdir}/libhdf4.settings
%{_includedir}/*.h
%dir %{_datadir}/hdf
%dir %{_datadir}/hdf/samples
%attr(644,root,root) %{_datadir}/hdf/samples/*

