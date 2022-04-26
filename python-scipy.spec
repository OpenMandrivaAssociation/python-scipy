# Can't mix clang (C/C++) and gcc (fortran) when using LTO
%global _disable_lto 1
%global Werror_cflags %nil

%define module	scipy

%bcond_without atlas
%bcond_with doc
%bcond_with pythran

%if %{with atlas}
%if %{_use_internal_dependency_generator}
%define __noautoreq 'lib(s|t)atlas\\.so\\..* 
%else
%define _requires_exceptions lib(s|t)atlas\.so\..*
%endif
%endif

Summary:	Scientific tools for Python
Name:		python-%{module}
Version:	1.7.3
Release:	2
Source0:	https://github.com/scipy/scipy/releases/download/v%{version}/scipy-%{version}.tar.xz
#Source1:	%{name}.rpmlintrc
License:	BSD
Group:		Development/Python
Url:		http://www.scipy.org
BuildRequires:	swig
BuildRequires:	amd-devel
%if %{with atlas}
BuildRequires:	libatlas-devel
%else
BuildRequires:	blas-devel
%endif
BuildRequires:	gcc-gfortran >= 4.0
BuildRequires:	pkgconfig(lapack)
BuildRequires:	pkgconfig(python3)
BuildRequires:	pkgconfig(netcdf)
BuildRequires:	python-numpy-f2py
BuildRequires:	python3dist(cython)
BuildRequires:	python3dist(pybind11) >= 2.4.0
BuildRequires:	python3dist(matplotlib)
BuildRequires:	python3dist(numpy) >= 1.9.2
BuildRequires:	python3dist(nose)
BuildRequires:	python3dist(setuptools)
%if %{with doc}
BuildRequires:	python3dist(sphinx)
BuildRequires:	python3dist(matplotlib)
BuildRequires:	python3dist(numpydoc)
%endif
%if %{with pythran}
BuildRequires:  pythran
%endif

BuildRequires:	suitesparse-devel
BuildRequires:	umfpack-devel
Requires:	python-numpy >= 1.9.2

Obsoletes:	python-SciPy
Obsoletes:	python-symeig

%description
SciPy is an open source library of scientific tools for Python. SciPy
supplements the popular numpy module, gathering a variety of high level
science and engineering modules together as a single package.

SciPy includes modules for graphics and plotting, optimization, integration,
special functions, signal and image processing, genetic algorithms, ODE 
solvers, and others.

%files
%doc LICENSE.txt
%dir %{py_platsitedir}/%{module}
%{py3_platsitedir}/%{module}/*
%{py3_platsitedir}/%{module}-*.egg-info

#---------------------------------------------------------------------------

%if %{with doc}
%package doc
Summary:	Documentation for scipy
Group:		Development/Python
BuildArch:	noarch

%description doc
This package contains documentation for Scipy

%files doc
%doc doc/build/html/*
%endif

#---------------------------------------------------------------------------

%prep
%autosetup -p1 -n %{module}-%{version}
find . -type f -name "*.py" -exec sed -i "s|#!/usr/bin/env python||" {} \;

cat > site.cfg << EOF
[amd]
library_dirs = %{_libdir}
include_dirs = /usr/include/suitesparse:/usr/include/ufsparse
amd_libs = amd

[umfpack]
library_dirs = %{_libdir}
include_dirs = /usr/include/suitesparse:/usr/include/ufsparse
umfpack_libs = umfpack
EOF

%build
%if ! %{with atlas}
%define extraflags "-DNO_ATLAS_INFO"
%endif
export SCIPY_USE_PYTHRAN=0%{?with_pythran}

# workaround for not using colorgcc when building due to colorgcc
# messes up output redirection..
env CC=clang CXX=clang++ PATH=${PATH#%{_datadir}/colorgcc:} \
CFLAGS="%{optflags} -fno-strict-aliasing -fno-lto" \
FFLAGS="$RPM_OPT_FLAGS -fPIC -fallow-argument-mismatch	" \
%if %{with atlas}
ATLAS=%{_libdir}/atlas \
%endif
FFTW=%{_libdir} \
BLAS=%{_libdir} \
LAPACK=%{_libdir} \
python setup.py config_fc --fcompiler=gnu95 --noarch build build_ext -lm

%install
export SCIPY_USE_PYTHRAN=0%{?with_pythran}
%py3_install

# Remove doc files that should be in %%doc:
rm -f %{buildroot}%{python3_sitearch}/%{pypi_name}/*.txt

%if %{with doc}
pushd doc
PYTHONPATH=%{buildroot}%{python3_sitearch}:%{python3_sitearch}:%{python3_sitelib} %__make html
popd
%endif

%check
pushd doc &> /dev/null
#PYTHONPATH=%{buildroot}%{py_platsitedir} python -c "import scipy; scipy.test()"
popd &> /dev/null

