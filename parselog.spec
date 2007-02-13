# TODO
# - cgi outputs just 'XML::API::XHTML=HASH(0x834c240)' instead of real html
#
%define		cgi_version 0.04
%define		main_version 0.09

# Conditional build:
%bcond_without	tests		# do not perform "make test"
#
%include	/usr/lib/rpm/macros.perl
%define		pdir parselog
%define		pnam cgi
Summary:	Parselog - a log file analysis tool
Summary(pl.UTF-8):	Parselog - narzędzie do analizy plików logów
Name:		parselog
Version:	%{main_version}
Release:	0.11
License:	GPL v2
Group:		Applications/System
Source0:	http://rekudos.net/repo/parselog/%{name}-%{main_version}.tar.gz
# Source0-md5:	bac806ec9981c9d363e709b42d9b129e
Source1:	http://rekudos.net/repo/parselog-cgi/%{name}-cgi-%{cgi_version}.tar.gz
# Source1-md5:	2942f30dd190dac31d7970ed04e0ffe5
Source2:	%{name}-apache.conf
Patch0:		%{name}-debug.patch
URL:		http://rekudos.net/parselog/
BuildRequires:	perl-DateTime
BuildRequires:	perl-LockFile-Simple
BuildRequires:	perl-devel >= 1:5.8.0
BuildRequires:	rpm-perlprov >= 4.1-13
BuildRequires:	rpmbuild(macros) >= 1.221
%if %{with tests}
BuildRequires:	perl-debug
%endif
Requires:	webapps
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_webapps	/etc/webapps
%define		_webapp		%{name}

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

%description -l pl.UTF-8
Parselog może tworzyć statystyki dla następujących aplikacji:
- AMaViS (i pochodne)
- Exim
- Postfix
- Apache
- MyDNS (wkrótce)

Powody, aby używać parseloga zamiast innych narzędzi do logów:
- prostota - jedno narzędzie dla wielu aplikacji,
- centralizacja - wyświetlanie razem wyników z wielu maszyn.

Powody, aby nie używać parseloga zamiast innych narzędzi:
- szybkość - parselog jest napisany w Perlu; narzędzie w C będzie
  szybsze,
- kompletność - parselog może nie liczyć w ten sam sposób, co inne
  narzędzie.

Ten pakiet zawiera zestaw modułów Perla i skrypt perlowy
przetwarzający różne pliki logów i tworzący bazy danych RRD.

%package cgi
Summary:	CGI script to generate graphs
Summary(pl.UTF-8):	Skrypt CGI generujący wykresy
Version:	%{cgi_version}
Group:		Applications/WWW
Requires:	%{name} = %{main_version}-%{release}

%description cgi
This package contains a Perl CGI script to generate on-the-fly graphs
to be viewed with a web browser.

%description cgi -l pl.UTF-8
Ten pakiet zawiera skrypt perlowy CGI generujący w locie wykresy
przeznaczone do oglądania przeglądarką WWW.

%prep
%setup -q -a 1
# for simplicity of build
mv parselog-cgi-%{cgi_version} cgi
%patch0 -p1

cd cgi
sed -i -e 's,/etc/parselog,%{_webapps}/%{_webapp},g' Makefile.PL bin/*.cgi conf/*.conf

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
install -d $RPM_BUILD_ROOT%{_webapps}/%{_webapp}
%{__make} install cgi \
	DESTDIR=$RPM_BUILD_ROOT

#mv $RPM_BUILD_ROOT{%{_sysconfdir}/parselog/{css,parselog-cgi.conf},%{_webapps}/%{_webapp}}
rm -f $RPM_BUILD_ROOT%{_bindir}/%{name}.cgi # duplicate
cp -p %{SOURCE2} $RPM_BUILD_ROOT%{_webapps}/%{_webapp}/httpd.conf
cp -p %{SOURCE2} $RPM_BUILD_ROOT%{_webapps}/%{_webapp}/apache.conf

rm -f $RPM_BUILD_ROOT%{perl_vendorarch}/auto/parselog/.packlist

%clean
rm -rf $RPM_BUILD_ROOT

%triggerin -- apache1 < 1.3.37-3, apache1-base
%webapp_register apache %{_webapp}

%triggerun -- apache1 < 1.3.37-3, apache1-base
%webapp_unregister apache %{_webapp}

%triggerin -- apache < 2.2.0, apache-base
%webapp_register httpd %{_webapp}

%triggerun -- apache < 2.2.0, apache-base
%webapp_unregister httpd %{_webapp}

%triggerpostun -- %{name}-cgi < 0.04-0.2
# rescue app configs.
for i in style.css parselog-cgi.conf; do
	if [ -f /etc/%{name}/$i.rpmsave ]; then
		mv -f %{_webapps}/%{_webapp}/$i{,.rpmnew}
		mv -f /etc/%{name}/$i.rpmsave %{_webapps}/%{_webapp}/$i
	fi
done

# migrate from apache-config macros
if [ -f /etc/%{name}/apache.conf.rpmsave ]; then
	if [ -d /etc/apache/webapps.d ]; then
		cp -f %{_webapps}/%{_webapp}/apache.conf{,.rpmnew}
		cp -f /etc/%{name}/apache.conf.rpmsave %{_webapps}/%{_webapp}/apache.conf
	fi

	if [ -d /etc/httpd/webapps.d ]; then
		cp -f %{_webapps}/%{_webapp}/httpd.conf{,.rpmnew}
		cp -f /etc/%{name}/apache.conf.rpmsave %{_webapps}/%{_webapp}/httpd.conf
	fi
	rm -f /etc/%{name}/apache.conf.rpmsave
fi

# migrating from earlier apache-config?
if [ -L /etc/apache/conf.d/09_%{name}.conf ]; then
	rm -f /etc/apache/conf.d/09_%{name}.conf
	/usr/sbin/webapp register apache %{_webapp}
	%service -q apache reload
fi
if [ -L /etc/httpd/httpd.conf/09_%{name}.conf ]; then
	rm -f /etc/httpd/httpd.conf/09_%{name}.conf
	/usr/sbin/webapp register httpd %{_webapp}
	%service -q httpd reload
fi

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
%dir %attr(750,root,http) %{_webapps}/%{_webapp}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_webapps}/%{_webapp}/apache.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_webapps}/%{_webapp}/httpd.conf
%attr(640,root,http) %config(noreplace) %verify(not md5 mtime size) %{_webapps}/%{_webapp}/parselog-cgi.conf
%dir %{_webapps}/%{_webapp}/css
%config(noreplace) %verify(not md5 mtime size) %{_webapps}/%{_webapp}/css/*
%attr(755,root,root) /usr/lib/cgi-bin/parselog.cgi
%{_mandir}/man1/parselog.cgi.1p*
/var/cache/parselog-cgi
