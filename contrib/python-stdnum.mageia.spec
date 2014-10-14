%define git_repo python-stdnum
%define git_head HEAD

Summary:	Python module to handle standardized numbers and codes
Name:		python-stdnum
Version:	%git_get_ver
Release:	%mkrel %git_get_rel2
Source:		%git_bs_source %{name}-%{version}.tar.gz
Source1:	%{name}-gitrpm.version
Source2:	%{name}-changelog.gitrpm.txt
License:	LGPLv2.1
Group:		Development/Python
Url:		http://arthurdejong.org/python-stdnum/
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildArch:	noarch
BuildRequires:	python-devel python-setuptools

%description
A Python module to parse, validate and reformat standard numbers and codes
in different formats.


%prep
%git_get_source
%setup -q

%build
PYTHONDONTWRITEBYTECODE= %__python setup.py build 

%install
%__rm -rf %{buildroot}
PYTHONDONTWRITEBYTECODE= %__python setup.py install --root=%{buildroot} --record=FILE_LIST
%__rm -rf docs/_build/html/.buildinfo

%clean
%__rm -rf %{buildroot}

%files -f FILE_LIST
%defattr(-,root,root)
%doc README NEWS ChangeLog COPYING

%changelog -f %{_sourcedir}/%{name}-changelog.gitrpm.txt
