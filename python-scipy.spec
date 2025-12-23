# Can't mix clang (C/C++) and gcc (fortran) when using LTO
%global _disable_lto 1
%global Werror_cflags %nil

%define module	scipy

# BLAS lib
%global blaslib flexiblas

# disable docs and tests on ABF
# the ~83675 tests this module contains takes an extraordinary length of time to complete
# many tests are also flaky and need to be disabled for the remainder of the test suite to pass
%bcond doc 0
%bcond tests 0

Summary:	Scientific tools for Python
Name:		python-%{module}
Version:	1.16.3
Release:	1
License:	BSD-3-Clause AND LGPL-2.0-or-later AND BSL-1.0
Group:		Development/Python
URL:		https://www.scipy.org
Source0:	https://github.com/scipy/scipy/releases/download/v%{version}/scipy-%{version}.tar.gz#/%{name}-%{version}.tar.gz
#Source1:	%%{name}.rpmlintrc

BuildRequires:	swig
BuildRequires:	amd-devel
BuildRequires:	gcc-gfortran >= 4.0
BuildRequires:	meson
BuildRequires:	ninja
BuildRequires:	pkgconfig
BuildRequires:	pkgconfig(%{blaslib})
BuildRequires:	pkgconfig(netcdf)
BuildRequires:	pkgconfig(python)
BuildRequires:	pkgconfig(xsimd)
BuildRequires:	pkgconfig(pybind11)
BuildRequires:	python-numpy-f2py
BuildRequires:	python%{pyver}dist(cython)
BuildRequires:	python%{pyver}dist(matplotlib)
BuildRequires:	python%{pyver}dist(meson-python)
BuildRequires:	python%{pyver}dist(nose)
BuildRequires:	python%{pyver}dist(numpy) >= 1.9.2
BuildRequires:  python%{pyver}dist(pip)
BuildRequires:	python%{pyver}dist(pybind11) >= 2.4.0
BuildRequires:  python%{pyver}dist(pythran)
BuildRequires:	python%{pyver}dist(setuptools)
BuildRequires:  python%{pyver}dist(wheel)
%if %{with tests}
BuildRequires:	python%{pyver}dist(hypothesis)
BuildRequires:	python%{pyver}dist(matplotlib)
BuildRequires:	python%{pyver}dist(pytest)
%endif
%if %{with doc}
BuildRequires:	python%{pyver}dist(sphinx)
BuildRequires:	python%{pyver}dist(matplotlib)
BuildRequires:	python%{pyver}dist(numpydoc)
%endif

BuildRequires:	suitesparse-devel
BuildRequires:	umfpack-devel
Requires:	python-numpy >= 1.9.2

Obsoletes:	python-SciPy
Obsoletes:	python-symeig

# Bug fix: https://github.com/scipy/scipy/pull/23940
%patchlist
https://github.com/scipy/scipy/pull/23940/commits/67974982d56f4bb73124aee47d506099182de188.patch


%description
SciPy is an open source library of scientific tools for Python. SciPy
supplements the popular numpy module, gathering a variety of high level
science and engineering modules together as a single package.

SciPy includes modules for graphics and plotting, optimization, integration,
special functions, signal and image processing, genetic algorithms, ODE 
solvers, and others.

%files
%license LICENSE.txt
%dir %{python_sitearch}/%{module}
%{python_sitearch}/%{module}/*
%{python_sitearch}/%{module}*.*-info

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
sed -i "s/    'blas=openblas',/    'blas=%{blaslib}',/" meson.build
sed -i "s/    'lapack=openblas'/    'lapack=%{blaslib}'/" meson.build
# https://github.com/mesonbuild/meson-python/issues/230 https://github.com/mesonbuild/meson-python/issues/235
sed -i "s/option('blas', type: 'string', value: 'openblas'/option('blas', type: 'string', value: '%{blaslib}'/" meson.options
sed -i "s/option('lapack', type: 'string', value: 'openblas'/option('lapack', type: 'string', value: '%{blaslib}'/" meson.options

# Do not do benchmarking, coverage, or timeout testing for RPM builds
sed -Ei '/^[[:blank:]]*"(asv|pytest-cov|pytest-timeout)"/d' pyproject.toml
# No scikit-umfpack in OMLx
sed -i '/^[[:blank:]]*"scikit-umfpack"/d' pyproject.toml
# Dont use pytest-xdist
sed -i '/^[[:blank:]]*"pytest-xdist"/d' pyproject.toml
# Loosen the upper bound on numpy
sed -i "/numpy/s/,<2\.6//" pyproject.toml
# Loosen the upper bound on Cython
sed -i '/Cython/s/,<[0-9.]\+//' pyproject.toml

%build
origpath="$PATH"
export CFLAGS="%{optflags} -fno-strict-aliasing"
export LDFLAGS="%{optflags} -lpython%{pyver}"
%py_build

%install
%py_install

# Remove doc files that should be in %%doc:
rm -f %{buildroot}%{python_sitearch}/%{pypi_name}/*.txt

%if %{with doc}
pushd doc
PYTHONPATH=%{buildroot}%{python_sitearch}:%{python_sitearch}:%{python_sitelib} %__make html
popd
%endif

%if %{with tests}
%check
export CI=true
export PYTHONPATH=%{buildroot}%{python_sitearch}:%{python_sitearch}:%{python_sitelib}

# TestDatasets try to download from the internet
skiptest="(TestDatasets)"
# (occasional) precision errors = flaky
skiptest+=" or (TestLinprogIPSpecific and test_solver_select)"
skiptest+=" or test_gh12922"
skiptest+=" or (TestPeriodogram and test_nd_axis_m1)"
skiptest+=" or (TestPeriodogram and test_nd_axis_0)"
skiptest+=" or (TestPdist and test_pdist_jensenshannon_iris)"
skiptest+=" or (test_rotation and test_align_vectors_single_vector)"
skiptest+=" or (test_lobpcg and test_tolerance_float32)"
skiptest+=" or (test_iterative and test_maxiter_worsening)"
skiptest+=" or (test_resampling and test_bootstrap_alternative)"
# fails on big endian
skiptest+=" or (TestNoData and test_nodata)"
# oom
skiptest+=" or (TestBSR and test_scalar_idx_dtype)"
# error while getting entropy
skiptest+=" or (test_cont_basic and 500-200-ncf-arg74)"
# https://github.com/scipy/scipy/issues/16927
skiptest+=" or (test_lobpcg and test_failure_to_run_iterations)"
%ifarch s390x
# gh#scipy/scipy#18878
skiptest+=" or (test_distance_transform_cdt05)"
skiptest+=" or (test_svd_maxiter)"
%endif
%ifarch riscv64
skiptest+=" or (TestSchur)"
skiptest+=" or (test_gejsv_general)"
skiptest+=" or (test_kendall_p_exact_large)"
skiptest+=" or (test_gejsv_edge_arguments)"
skiptest+=" or (test_gh12999)"
skiptest+=" or (test_propack)"
skiptest+=" or (test_milp)"
skiptest+=" or (test_gejsv_NAG)"
%endif
# not enough precison on 32 bits
if [ $(getconf LONG_BIT) -eq 32 ]; then
    skiptest+=" or (TestCheby1 and test_basic)"
    skiptest+=" or test_extreme_entropy"
fi
# Ignoring the datasets tests
skiptest+=" or test_data"
# Flaky tests
skiptest+=" or (test_all_data_read_overlap and test_all_data_read_bad_checksum)"
echo $PWD

pushd %{buildroot}/%{python_sitearch}
	pytest -v --ignore="scipy/datasets/tests/test_data.py" --ignore="scipy/stats/tests/test_continuous.py" \
	--ignore="scipy/io/matlab/tests/test_streams.py" -k "not $skiptest" scipy/ --numprocesses=auto
	# Remove test remnants
	rm -rf gram{A,B}
	rm -rf .pytest_cache
popd
%endif
