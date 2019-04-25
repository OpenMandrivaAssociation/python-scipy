%define enable_atlas 1
%{?_with_atlas: %global enable_atlas 1}
%define Werror_cflags %nil
%define _disable_lto 1

%if %enable_atlas
%if %{_use_internal_dependency_generator}
%define __noautoreq 'lib(s|t)atlas\\.so\\..* 
%else
%define _requires_exceptions lib(s|t)atlas\.so\..*
%endif
%endif

%define module	scipy

Summary:	Scientific tools for Python
Name:		python-%{module}
Version:	1.2.1
Release:	1
Source0:	https://github.com/scipy/scipy/releases/download/v%{version}/scipy-%{version}.tar.xz
Source1:	%{name}.rpmlintrc
License:	BSD
Group:		Development/Python
Url:		http://www.scipy.org
Obsoletes:	python-SciPy
Obsoletes:	python-symeig
Requires:	python-numpy >= 1.5
BuildRequires:	swig
%if %enable_atlas
BuildRequires:	libatlas-devel
%else
BuildRequires:	blas-devel
%endif 
BuildRequires:	pkgconfig(lapack)
BuildRequires:	python-numpy-devel >= 1.5
BuildRequires:	gcc-gfortran >= 4.0
BuildRequires:	netcdf-devel
BuildRequires:	python3-devel
BuildRequires:	python-nose
BuildRequires:	amd-devel
BuildRequires:	umfpack-devel
BuildRequires:	python-sphinx
BuildRequires:	python-matplotlib
BuildRequires:	python-setuptools

%description
SciPy is an open source library of scientific tools for Python. SciPy
supplements the popular numpy module, gathering a variety of high level
science and engineering modules together as a single package.

SciPy includes modules for graphics and plotting, optimization, integration,
special functions, signal and image processing, genetic algorithms, ODE 
solvers, and others.

%package -n python2-%{module}
Summary:        Scientific tools for Python
BuildRequires:	python2-devel
BuildRequires:	python2-setuptools
BuildRequires:	python2-nose
BuildRequires:	python2-matplotlib
BuildRequires:	python2-numpy-devel

%description -n python2-%{module}
SciPy is an open source library of scientific tools for Python. SciPy
supplements the popular numpy module, gathering a variety of high level
science and engineering modules together as a single package.

SciPy includes modules for graphics and plotting, optimization, integration,
special functions, signal and image processing, genetic algorithms, ODE
solvers, and others.

%prep
%setup -q -n %{module}-%{version}
%apply_patches

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

cp -a . %{py2dir}

%build
# workaround for not using colorgcc when building due to colorgcc
# messes up output redirection..
PATH=${PATH#%{_datadir}/colorgcc:} \
CFLAGS="%{optflags} -fno-strict-aliasing -fno-lto" \
ATLAS=%{_libdir}/atlas \
FFTW=%{_libdir} \
BLAS=%{_libdir} \
LAPACK=%{_libdir} \
python setup.py config_fc --fcompiler=gnu95 --noarch build build_ext -lm

pushd %py2dir
PATH=${PATH#%{_datadir}/colorgcc:} \
CFLAGS="%{optflags} -fno-strict-aliasing -fno-lto" \
ATLAS=%{_libdir}/atlas \
FFTW=%{_libdir} \
BLAS=%{_libdir} \
LAPACK=%{_libdir} \
python2 setup.py config_fc --fcompiler=gnu95 --noarch build build_ext -lm


%install
# workaround for not using colorgcc when building due to colorgcc
# messes up output redirection..
PATH=${PATH#%{_datadir}/colorgcc:}

python setup.py install --prefix=%{_prefix} --root=%{buildroot}
find %{buildroot}%{python_sitearch}/scipy -type d -name tests | xargs rm -rf # Don't ship tests
# Don't ship weave examples, they're marked as documentation:
find %{buildroot}%{python_sitearch}/scipy/weave -type d -name examples | xargs rm -rf
# fix executability issue
chmod +x %{buildroot}%{python_sitearch}/%{module}/io/arff/arffread.py
chmod +x %{buildroot}%{python_sitearch}/%{module}/special/spfun_stats.py

pushd %py2dir
python2 setup.py install --prefix=%{_prefix} --root=%{buildroot}
find %{buildroot}%{python2_sitearch}/scipy -type d -name tests | xargs rm -rf # Don't ship tests
# Don't ship weave examples, they're marked as documentation:
find %{buildroot}%{python2_sitearch}/scipy/weave -type d -name examples | xargs rm -rf
# fix executability issue
chmod +x %{buildroot}%{python2_sitearch}/%{module}/io/arff/arffread.py
chmod +x %{buildroot}%{python2_sitearch}/%{module}/special/spfun_stats.py



%check
pushd doc &> /dev/null
PYTHONPATH=%{buildroot}%{py_platsitedir} python -c "import scipy; scipy.test()"
popd &> /dev/null

%files
%doc doc/README.txt THANKS.txt LICENSE.txt
%dir %{py_platsitedir}/%{module}
%{py_platsitedir}/%{module}/*
%{py_platsitedir}/%{module}-*.egg-info

%files -n python2-%{module}
%doc doc/README.txt THANKS.txt LICENSE.txt
%dir %{py2_platsitedir}/%{module}
%{py2_platsitedir}/%{module}/*
%{py2_platsitedir}/%{module}-*.egg-info
