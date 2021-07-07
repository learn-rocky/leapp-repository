%global leapp_datadir %{_datadir}/leapp-repository
%global repositorydir %{leapp_datadir}/repositories
%global custom_repositorydir %{leapp_datadir}/custom-repositories

%define leapp_repo_deps  5

%if 0%{?rhel} == 7
    %define leapp_python_sitelib %{python2_sitelib}
%else
    %define leapp_python_sitelib %{python3_sitelib}
%endif


# TODO: not sure whether it's required nowadays. Let's check it and drop
# the whole block if not.
%if 0%{?rhel} == 7
# Defining py_byte_compile macro because it is not defined in old rpm (el7)
# Only defined to python2 since python3 is not used in RHEL7
%{!?py_byte_compile: %global py_byte_compile py2_byte_compile() {\
    python_binary="%1"\
    bytecode_compilation_path="%2"\
    find $bytecode_compilation_path -type f -a -name "*.py" -print0 | xargs -0 $python_binary -c 'import py_compile, sys; [py_compile.compile(f, dfile=f.partition("$RPM_BUILD_ROOT")[2]) for f in sys.argv[1:]]' || :\
    find $bytecode_compilation_path -type f -a -name "*.py" -print0 | xargs -0 $python_binary -O -c 'import py_compile, sys; [py_compile.compile(f, dfile=f.partition("$RPM_BUILD_ROOT")[2]) for f in sys.argv[1:]]' || :\
}\
py2_byte_compile "%1" "%2"}
%endif


Name:           leapp-repository
Version:        0.14.0
Release:        1%{?dist}
Summary:        Repositories for leapp

License:        ASL 2.0
URL:            https://oamg.github.io/leapp/
Source0:        https://github.com/oamg/%{name}/archive/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
Source1:        deps-pkgs.tar.gz
BuildArch:      noarch

%if 0%{?rhel} && 0%{?rhel} == 7
######### RHEL 7 ############
BuildRequires:  python-devel
Requires:       python2-leapp

# We should not drop this on RHEL 7 because of the compatibility reasons
Obsoletes:      leapp-repository-data <= 0.6.1
Provides:       leapp-repository-data <= 0.6.1

# Former leapp subpackage that is part of the sos package since HEL 7.8
Obsoletes:      leapp-repository-sos-plugin <= 0.9.0

%else
######### RHEL 8 ############
BuildRequires:  python3-devel
Requires:       python3-leapp
%global __requires_exclude ^python\\(abi\\) = 3\\..+|/usr/libexec/platform-python

%endif

# IMPORTANT: everytime the requirements are changed, increment number by one
# - same for Provides in deps subpackage
Requires:       leapp-repository-dependencies = %{leapp_repo_deps}

# IMPORTANT: this is capability provided by the leapp framework rpm.
# Check that 'version' instead of the real framework rpm version.
Requires:       leapp-framework >= 2.0, leapp-framework < 3


%description
Repositories for leapp


# This metapackage should contain all RPM dependencies exluding deps on *leapp*
# RPMs. This metapackage will be automatically replaced during the upgrade
# to satisfy dependencies with RPMs from target system.
%package deps
Summary:    Meta-package with system dependencies of %{name} package

# IMPORTANT: everytime the requirements are changed, increment number by one
# - same for Requires in main package
Provides:  leapp-repository-dependencies = %{leapp_repo_deps}
##################################################
# Real requirements for the leapp-repository HERE
##################################################
Requires:   dnf >= 4
Requires:   pciutils
%if 0%{?rhel} && 0%{?rhel} == 7
# Required to gather system facts about SELinux
Requires:   libselinux-python
Requires:   python-pyudev
# required by SELinux actors
Requires:   policycoreutils-python
# Required to fetch leapp data
Requires:   python-requests

%else
############# RHEL 8 dependencies (when the source system is RHEL 8) ##########
# systemd-nspawn utility
Requires:   systemd-container
Requires:   python3-pyudev
# Required to fetch leapp data
Requires:   python3-requests
# Required because the code is kept Py2 & Py3 compatible
Requires:   python3-six
# required by SELinux actors
Requires:   policycoreutils-python-utils
%endif
##################################################
# end requirement
##################################################


%description deps
%{summary}


%prep
%autosetup -n %{name}-%{version}
%setup -q  -n %{name}-%{version} -D -T -a 1


%build
%if 0%{?rhel} == 7
cp -a leapp*deps-el8*rpm repos/system_upgrade/el7toel8/files/bundled-rpms/
%else
cp -a leapp*deps-el9*rpm repos/system_upgrade/el8toel9/files/bundled-rpms/
%endif


%install
install -m 0755 -d %{buildroot}%{custom_repositorydir}
install -m 0755 -d %{buildroot}%{repositorydir}
cp -r repos/* %{buildroot}%{repositorydir}/
install -m 0755 -d %{buildroot}%{_sysconfdir}/leapp/repos.d/
install -m 0755 -d %{buildroot}%{_sysconfdir}/leapp/transaction/
install -m 0755 -d %{buildroot}%{_sysconfdir}/leapp/files/
install -m 0644 etc/leapp/transaction/* %{buildroot}%{_sysconfdir}/leapp/transaction

# install CLI commands for the leapp utility on the expected path
install -m 0755 -d %{buildroot}%{leapp_python_sitelib}/leapp/cli/
cp -r commands %{buildroot}%{leapp_python_sitelib}/leapp/cli/

# Remove irrelevant repositories - We don't want to ship them for the particular
# RHEL version
%if 0%{?rhel} == 7
rm -rf %{buildroot}%{repositorydir}/system_upgrade/el8toel9
%else
rm -rf %{buildroot}%{repositorydir}/system_upgrade/el7toel8
%endif

# remove component/unit tests, Makefiles, ... stuff that related to testing only
rm -rf %{buildroot}%{repositorydir}/common/actors/testactor
find %{buildroot}%{repositorydir}/common -name "test.py" -delete
rm -rf `find %{buildroot}%{repositorydir} -name "tests" -type d`
find %{buildroot}%{repositorydir} -name "Makefile" -delete

for DIRECTORY in $(find  %{buildroot}%{repositorydir}/  -mindepth 1 -maxdepth 1 -type d);
do
    REPOSITORY=$(basename $DIRECTORY)
    echo "Enabling repository $REPOSITORY"
    ln -s  %{repositorydir}/$REPOSITORY  %{buildroot}%{_sysconfdir}/leapp/repos.d/$REPOSITORY
done;

# __python2 could be problematic on systems with Python3 only, but we have
# no choice as __python became error on F33+:
#   https://fedoraproject.org/wiki/Changes/PythonMacroError
%if 0%{?rhel} == 7
%py_byte_compile %{__python2} %{buildroot}%{repositorydir}/*
%else
%py_byte_compile %{__python3} %{buildroot}%{repositorydir}/*
%endif


%files
%doc README.md
%license LICENSE
%dir %{_sysconfdir}/leapp/transaction
%dir %{_sysconfdir}/leapp/files
%dir %{leapp_datadir}
%dir %{repositorydir}
%dir %{custom_repositorydir}
%dir %{leapp_python_sitelib}/leapp/cli/commands
%{_sysconfdir}/leapp/repos.d/*
%{_sysconfdir}/leapp/transaction/*
%{repositorydir}/*
%{leapp_python_sitelib}/leapp/cli/commands/*


%files deps
# no files here


# DO NOT TOUCH SECTION BELOW IN UPSTREAM
%changelog
* Mon Apr 16 2018 Vinzenz Feenstra <evilissimo@redhat.com> - %{version}-%{release}
- Initial RPM
