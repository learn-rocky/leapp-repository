# The %%{rhel} macro just has to be specified
%global  lrdname  leapp-repository-deps-el%{rhel}
%global  ldname   leapp-deps-el%{rhel}

%define leapp_repo_deps  5
%define leapp_framework_deps   3

# NOTE: the Version contains the %{rhel} macro just for the convenience to
# have always upgrade path between newer and older deps packages. So for
# packages built for RHEL 8 it's 5.0.8, for RHEL 9 it's 5.0.9, etc..
# Not sure how much it will be beneficial in the end, but why not?

# TODO: keeping the name of the specfile & srpm leapp-el7toel8-deps even when
# it could be confusing as we start to build for el8toel9.
Name:       leapp-el7toel8-deps
Version:    5.0.%{rhel}
Release:    1%{?dist}
Summary:    Dependencies for *leapp* packages
BuildArch:  noarch

License:    ASL 2.0
URL:        https://oamg.github.io/leapp/

%description
%{summary}

##################################################
# DEPS FOR LEAPP REPOSITORY ON RHEL 8+ (IPU target system)
##################################################
%package -n %{lrdname}
Summary:    Meta-package with system dependencies for leapp repository
Provides:   leapp-repository-dependencies = %{leapp_repo_deps}
Obsoletes:  leapp-repository-deps

Requires:   dnf >= 4
Requires:   pciutils
Requires:   python3
Requires:   python3-pyudev
# required by SELinux actors
Requires:   policycoreutils-python-utils

%description -n %{lrdname}
%{summary}

##################################################
# DEPS FOR LEAPP FRAMEWORK ON RHEL 8+ (IPU target system)
##################################################
%package -n %{ldname}
Summary:    Meta-package with system dependencies for leapp framework
Provides:   leapp-framework-dependencies = %{leapp_framework_deps}
Obsoletes:  leapp-deps

Requires:   findutils

%if 0%{?rhel} == 8
# Keep currently these dependencies as maybe we would need them to finish the
# RPMUpgradePhase phase correctly (e.g. postun scriptlets would need py2)
Requires:   python2-six
Requires:   python2-setuptools
Requires:   python2-requests
%endif

# Python3 deps
Requires:   python3-six
Requires:   python3-setuptools
Requires:   python3-requests

%description -n %{ldname}
%{summary}

%prep

%build

%install

# do not create main packages
#%files

%files -n %{lrdname}
# no files here

%files -n %{ldname}
# no files here

%changelog
* Tue Jan 22 2019 Petr Stodulka <pstodulk@redhat.com> - %{version}-%{release}
- Initial rpm
