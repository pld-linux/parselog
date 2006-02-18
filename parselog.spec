%define		cgi_version 0.04

# Conditional build:
%bcond_with	tests		# do not perform "make test"
#
%include	/usr/lib/rpm/macros.perl
Summary:	Parselog - a log file analysis tool
Summary(pl):	Parselog - narzêdzie do analizy plików logów
Name:		parselog
Version:	0.09
Release:	0.1
Epoch:		0
License:	GPL v2
Group:		Applications/System
Source0:	http://rekudos.net/repo/parselog/%{name}.tgz
# Source0-md5:	bac806ec9981c9d363e709b42d9b129e
Source1:	http://rekudos.net/repo/parselog-cgi/%{name}-cgi.tgz
# Source1-md5:	2942f30dd190dac31d7970ed04e0ffe5
URL:		http://rekudos.net/parselog/
BuildRequires:	perl-DateTime
BuildRequires:	perl-LockFile-Simple
BuildRequires:	perl-devel >= 1:5.8.0
BuildRequires:	rpm-perlprov >= 4.1-13
BuildRequires:	rpmbuild(macros) >= 1.221
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Parselog can produce statistics for the following applications
- AMaViS (and derivatives)
- Exim
- Postfix
- Apache
- MyDNS (coming soon)

Reasons to use parselog instead of other log tools:
- Simplicity - Install one tool too cover multiple applications,
- Centralisation - display results from multiple machines together.

Reasons for not using parselog of other log tools:
- Speed - parselog is written in Perl. Your 'C'-based tool will be
  faster,
- Completeness - maybe parselog doesn't measure the same way other
  tools do.

This package contains a set of Perl modules and a Perl script that
will parse various log files and create Round Robin Databases (RRDs).

%description -l pl
Parselog mo¿e tworzyæ statystyki dla nastêpuj±cych aplikacji:
- AMaViS (i pochodne)
- Exim
- Postfix
- Apache
- MyDNS (wkrótce)

Powody, aby u¿ywaæ parseloga zamiast innych narzêdzi do logów:
- prostota - jedno narzêdzie dla wielu aplikacji,
- centralizacja - wy¶wietlanie razem wyników z wielu maszyn.

Powody, aby nie u¿ywaæ parseloga zamiast innych narzêdzi:
- szybko¶æ - parselog jest napisany w Perlu; narzêdzie w C bêdzie
  szybsze,
- kompletno¶æ - parselog mo¿e nie liczyæ w ten sam sposób, co inne
  narzêdzie.

Ten pakiet zawiera zestaw modu³ów Perla i skrypt perlowy
przetwarzaj±cy ró¿ne pliki logów i tworz±cy bazy danych RRD.

%package cgi
Summary:	CGI script to generate graphs
Summary(pl):	Skrypt CGI generuj±cy wykresy
Group:		Applications/WWW
Requires:	%{name} = %{version}-%{release}
Version:	%{cgi_version}

%description cgi
This package contains a Perl CGI script to generate on-the-fly graphs
to be viewed with a web browser.

%description cgi -l pl
Ten pakiet zawiera skrypt perlowy CGI generuj±cy w locie wykresy
przeznaczone do ogl±dania przegl±dark± WWW.

%prep
%setup -q -a 1

# for simplicity of build
mv parselog-cgi-%{cgi_version} cgi

%build
%{__perl} Makefile.PL \
	INSTALLDIRS=vendor
%{__make} \
	OPTIMIZE="%{rpmcflags}"
%{?with_tests:%{__make} test}

cd cgi
%{__perl} Makefile.PL \
	INSTALLDIRS=vendor
%{__make} \
	OPTIMIZE="%{rpmcflags}"
%{?with_tests:%{__make} test}

%install
rm -rf $RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT{%{_sbindir},/var/cache/parselog-cgi}
%{__make} install dirs etc \
	DESTDIR=$RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT%{_examplesdir}/%{name}-%{version}
mv $RPM_BUILD_ROOT{%{_bindir},%{_sbindir}}/parselog
cp -a example $RPM_BUILD_ROOT%{_examplesdir}/%{name}-%{version}
install conf/conf.d/* $RPM_BUILD_ROOT%{_sysconfdir}/parselog/conf.d

cd cgi
%{__make} install cgi \
	DESTDIR=$RPM_BUILD_ROOT

rm -f $RPM_BUILD_ROOT%{_bindir}/%{name}.cgi # duplicate
cp -p conf/apache.conf $RPM_BUILD_ROOT%{_sysconfdir}/parselog/apache.conf

%clean
rm -rf $RPM_BUILD_ROOT

%triggerin cgi -- apache1 >= 1.3.33-2
%apache_config_install -v 1 -c %{_sysconfdir}/parselog/apache.conf -n 09

%triggerun cgi -- apache1 >= 1.3.33-2
%apache_config_uninstall -v 1 -n 09

%triggerin cgi -- apache >= 2.0.0
%apache_config_install -v 2 -c %{_sysconfdir}/parselog/apache.conf -n 09

%triggerun cgi -- apache >= 2.0.0
%apache_config_uninstall -v 2 -n 09

%files
%defattr(644,root,root,755)
%doc Changes README
%dir %{_sysconfdir}/parselog
%dir %{_sysconfdir}/parselog/conf.d
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/parselog/parselog.conf
%config(noreplace,missingok) %verify(not md5 mtime size) %{_sysconfdir}/parselog/conf.d/*

%attr(755,root,root) %{_sbindir}/parselog

%{_mandir}/man1/parselog.1p*
%{_mandir}/man3/*

%{perl_vendorlib}/Log/Parse.pm
%{perl_vendorlib}/Log/Read.pm

%dir %{perl_vendorlib}/Log/Read
%{perl_vendorlib}/Log/Read/Apache.pm
%{perl_vendorlib}/Log/Read/Exim.pm
%{perl_vendorlib}/Log/Read/Syslog.pm

%dir /var/lib/parselog

%{_examplesdir}/%{name}-%{version}

%files cgi
%defattr(644,root,root,755)
%doc cgi/{Changes,README}
%dir %{_sysconfdir}/parselog/css
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/parselog/css/*
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/parselog/apache.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/parselog/parselog-cgi.conf
%attr(755,root,root) /usr/lib/cgi-bin/parselog.cgi
%{_mandir}/man1/parselog.cgi.1p*
/var/cache/parselog-cgi
