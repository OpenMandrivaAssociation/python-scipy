# Can't mix clang (C/C++) and gcc (fortran) when using LTO
%global _disable_lto 1
%global Werror_cflags %nil

%define module	scipy

# BLAS lib
%global blaslib flexiblas

%bcond_with doc
%bcond_with pythran

Summary:	Scientific tools for Python
Name:		python-%{module}
Version:	1.11.4
Release:	1
Source0:	https://github.com/scipy/scipy/releases/download/v%{version}/scipy-%{version}.tar.gz
#Source1:	%{name}.rpmlintrc
License:	BSD
Group:		Development/Python
Url:		https://www.scipy.org
BuildRequires:	swig
BuildRequires:	amd-devel
BuildRequires:	pkgconfig(%{blaslib})
BuildRequires:	gcc-gfortran >= 4.0
BuildRequires:	pkgconfig(python3)
BuildRequires:	pkgconfig(netcdf)
BuildRequires:	python-numpy-f2py
BuildRequires:	python%{pyver}dist(cython)
BuildRequires;	python%{pyver}dist(meson-python)
BuildRequires:	python%{pyver}dist(matplotlib)
BuildRequires:	python%{pyver}dist(numpy) >= 1.9.2
BuildRequires:	python%{pyver}dist(nose)
BuildRequires:	python%{pyver}dist(pybind11) >= 2.4.0
BuildRequires:	python%{pyver}dist(setuptools)
%if %{with doc}
BuildRequires:	python%{pyver}dist(sphinx)
BuildRequires:	python%{pyver}dist(matplotlib)
BuildRequires:	python%{pyver}dist(numpydoc)
%endif
%if %{with pythran}
BuildRequires:  python%{pyver}dist(pythran)
%endif

BuildRequires:	suitesparse-devel
BuildRequires:	umfpack-devel
Requires:	python-numpy >= 1.9.2

Obsoletes:	python-SciPy
Obsoletes:	python-symeig

%patchlist
https://github.com/scipy/scipy/commit/ab7d08c6148286059f6498ab5c3070268d13cbd9.patch

%description
SciPy is an open source library of scientific tools for Python. SciPy
supplements the popular numpy module, gathering a variety of high level
science and engineering modules together as a single package.

SciPy includes modules for graphics and plotting, optimization, integration,
special functions, signal and image processing, genetic algorithms, ODE 
solvers, and others.

%files
%license LICENSE.txt
%dir %{py_platsitedir}/%{module}
%{py3_platsitedir}/%{module}/*
%{py3_platsitedir}/%{module}*.*-info

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

# BLAS
cat >> pyproject.toml << EOF

[tool.meson-python.args]
setup = ['-Dblas=%{blaslib}', '-Dlapack=%{blaslib}'%{!?with_pythran:, '-Duse-pythran=false'}]
EOF


%build
%py_build

%install
%py_install

# Remove doc files that should be in %%doc:
rm -f %{buildroot}%{python3_sitearch}/%{pypi_name}/*.txt

%if %{with doc}
pushd doc
PYTHONPATH=%{buildroot}%{python3_sitearch}:%{python3_sitearch}:%{python3_sitelib} %__make html
popd
%endif

%check
pushd doc &> /dev/null
PYTHONPATH=%{buildroot}%{py_platsitedir} python -c "import scipy; scipy.test()"
popd &> /dev/null

