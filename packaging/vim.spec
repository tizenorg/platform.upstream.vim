%define pkg_version 7.3
%define official_ptchlvl 822
%define VIM_SUBDIR vim73
%define site_runtimepath /usr/share/vim/site

Name:           vim
Version:        7.3
Release:        0
License:        VIM LICENSE
#
Summary:        Vi IMproved
#
Url:            http://www.vim.org/
Group:          Base/Utilities
Source:         ftp://ftp.vim.org/pub/vim/unix/vim-7.3.tar.bz2
Source3:        tizen.vimrc
Source98:       %{name}-7.3-patches.tar.bz2
Source99:       %{name}-7.3-rpmlintrc
Source1001: 	vim.manifest
BuildRequires:  autoconf
BuildRequires:  db4-devel
BuildRequires:  fdupes
BuildRequires:  gettext-devel
BuildRequires:  ncurses-devel
BuildRequires:  perl
BuildRequires:  pkgconfig
BuildRequires:  python-devel
BuildRequires:  systemd
Requires(pre):         update-alternatives
#
Provides:       vi
Provides:       vim_client
#
%define vim_prereq %{name}-base = %{version}
# Explicitly require versioned perl for libperl.so
%define perl_requires perl = %(rpm -q --qf '%{VERSION}' perl)
Requires(pre):         %{vim_prereq}

%description
Vim (Vi IMproved) is an almost compatible version of the UNIX editor
vi. Almost every possible command can be performed using only ASCII
characters. Only the 'Q' command is missing (you do not need it). Many
new features have been added: multilevel undo, command line history,
file name completion, block operations, and editing of binary data.

Vi is available for the AMIGA, MS-DOS, Windows NT, and various versions
of UNIX.

Package vim contains the normal version of vim. To get the full runtime
environment install additionally vim-data.

%package data
Summary:        Vi IMproved
BuildArch:      noarch
Requires(pre):         %{vim_prereq}

%description data
Vim (Vi IMproved) is an almost compatible version of the UNIX editor
vi. Almost every possible command can be performed using only ASCII
characters. Only the 'Q' command is missing (you do not need it). Many
new features have been added: multilevel undo, command line history,
file name completion, block operations, and editing of binary data.

Vi is available for the AMIGA, MS-DOS, Windows NT, and various versions
of UNIX.

Package vim-data contains the runtime files.

%package base
Summary:        Vi IMproved
Requires(pre):         %{vim_prereq}
Requires(pre):         update-alternatives

%description base
Vim (Vi IMproved) is an almost compatible version of the UNIX editor
vi. Almost every possible command can be performed using only ASCII
characters. Only the 'Q' command is missing (you do not need it). Many
new features have been added: multilevel undo, command line history,
file name completion, block operations, and editing of binary data.

Vi is available for the AMIGA, MS-DOS, Windows NT, and various versions
of UNIX.

For SUSE Linux, Vim is used as /usr/bin/vi.

Package vim-base contains the common files needed for all different vim
versions. You still need to select at least one of the vim,
vim-enhanced or gvim packages. For full runtime support you might also
want to install the vim-data package.

%package enhanced
Summary:        A version of the VIM editor which includes recent enhancements
Requires:       %{perl_requires}
Requires:       vim-data
Provides:       vi
Provides:       vim_client
Requires(pre):         %{vim_prereq}
Requires(pre):         update-alternatives

%description enhanced
The vim-enhanced package contains a version of VIM with extra, recently
introduced features like Ruby, Perl and TCL interpreters, but it has no
graphical user interface. Please use gvim instead, if you need a gui
too.

Install the vim-enhanced package if you'd like to use a version of the
VIM editor which includes recently added enhancements like interpreters
for the Python and Perl scripting languages. You'll also need to
install the base package 'vim', for online help, etc. If you need the
graphical features of vim, you might want to install package gvim too.

%prep
%setup -q -n vim73 -b 98
cp %{SOURCE1001} .
for p in ../vim-%{pkg_version}-patches/%{pkg_version}*; do
    test -e $p || break
    test ${p#*/%{pkg_version}.} -le %{official_ptchlvl} || exit 1
    echo Patch $p
    patch -s -p0 < $p
done
unset p
cp %{SOURCE3}  .

# newer perl? ugly hack to fix build anyway.
sed -i -e 's/^XS(XS_/XS_INTERNAL(XS_/' src/if_perl.xs

%build
export CFLAGS="%{optflags} -Wall -pipe -fno-strict-aliasing"
export CFLAGS=${CFLAGS/-D_FORTIFY_SOURCE=2/-D_FORTIFY_SOURCE=1}

export COMMON_OPTIONS="\
    --with-vim-name=vim \
    --with-ex-name=ex \
    --with-view-name=view \
    --enable-cscope \
    --enable-multibyte \
    --enable-sniff \
    --with-features=huge \
    --with-compiledby='http://www.tizen.org/' \
    --with-tlib=tinfo \
    --with-global-runtime=%{site_runtimepath}"
export SCRIPT_OPTIONS="\
    --enable-perlinterp \
    --enable-pythoninterp \
    --with-python-config-dir=%{py_libdir}/config"

pushd src
autoconf
popd
#
# build small default binary
%configure \
    ${COMMON_OPTIONS} --disable-gui --without-x --disable-gpm \
    --disable-perlinterp --disable-pythoninterp \
    --disable-rubyinterp --disable-tclinterp
sed -i -e 's|define HAVE_DATE_TIME 1|undef HAVE_DATE_TIME|' src/auto/config.h
make VIMRCLOC=/etc VIMRUNTIMEDIR=/usr/share/vim/current MAKE="make -e" %{?jobs:-j%jobs}
cp src/vim vim-normal
make distclean
#
# build enhanced binary
%configure ${COMMON_OPTIONS} ${SCRIPT_OPTIONS} --disable-gui
sed -i -e 's|define HAVE_DATE_TIME 1|undef HAVE_DATE_TIME|' src/auto/config.h
make VIMRCLOC=/etc VIMRUNTIMEDIR=/usr/share/vim/current MAKE="make -e" %{?jobs:-j%jobs}
cp src/vim vim-enhanced
#make distclean
#
#

%install
# create icon directory to have the icon from the tarball installed
install -d -m 0755 %{buildroot}%{_datadir}/icons/hicolor/48x48/apps

cd src
make install DESTDIR=%{buildroot} BINDIR=%{_bindir} VIMRCLOC=/etc VIMRUNTIMEDIR=%{site_runtimepath}
cd ..

# install the other binaries
install -D -m 0755 vim-normal    %{buildroot}/%{_bindir}/vim-normal
install -D -m 0755 vim-enhanced  %{buildroot}%{_bindir}/vim-enhanced

# compat symlinks
# we need a dummy target for /etc/alternatives/vim
mkdir -p %{buildroot}%{_sysconfdir}/alternatives
touch %{buildroot}%{_sysconfdir}/alternatives/vim
ln -s -f /etc/alternatives/vim %{buildroot}/%{_bindir}/vim

ln -s -f vim   %{buildroot}%{_bindir}/vi
ln -s -f vim        %{buildroot}%{_bindir}/edit
ln -s -f vim       %{buildroot}/%{_bindir}/ex

# man pages
mkdir -p %{buildroot}%{_mandir}/man1
ln -s -f vim.1.gz %{buildroot}%{_mandir}/man1/vi.1.gz
ln -s -f vim.1.gz %{buildroot}%{_mandir}/man1/ex.1.gz


# make the vim settings more generic
ln -s -f %{VIM_SUBDIR} %{buildroot}%{_datadir}/vim/current

# additional files
install -D -m 0644 %{SOURCE3} %{buildroot}%{_sysconfdir}/vimrc

# create site wide runtime directory
mkdir -p -m 0755 %{buildroot}%{site_runtimepath}/after
mkdir -m 0755 %{buildroot}%{site_runtimepath}/autoload
mkdir -m 0755 %{buildroot}%{site_runtimepath}/colors
mkdir -m 0755 %{buildroot}%{site_runtimepath}/doc
mkdir -m 0755 %{buildroot}%{site_runtimepath}/plugin
mkdir -m 0755 %{buildroot}%{site_runtimepath}/syntax
mkdir -m 0755 %{buildroot}%{site_runtimepath}/ftdetect
mkdir -m 0755 %{buildroot}%{site_runtimepath}/after/syntax
mkdir -m 0755 %{buildroot}%{_datadir}/vim/current/skeletons
mkdir -m 0755 %{buildroot}%{_sysconfdir}/skel


#
# documentation
install -d -m 0755 %{buildroot}%{_docdir}/{,g}vim/
cp runtime/doc/uganda.txt LICENSE
install -D -m 0644 \
    tizen.vimrc \
    README.txt README_src.txt README_unix.txt \
  %{buildroot}%{_docdir}/vim/
#
# remove unecessary duplicate manpages
rm -rf %{buildroot}%{_mandir}/fr.ISO8859-1/
rm -rf %{buildroot}%{_mandir}/fr.UTF-8/
rm -rf %{buildroot}%{_mandir}/pl.ISO8859-2/
rm -rf %{buildroot}%{_mandir}/pl.UTF-8/
rm -rf %{buildroot}%{_mandir}/ru.KOI8-R/
rm -rf %{buildroot}%{_mandir}/it.ISO8859-1/
rm -rf %{buildroot}%{_mandir}/it.UTF-8/
rm -rf %{buildroot}%{_mandir}/ru.UTF-8
# and move russian manpages to a place where they can be found
rm -rf %{buildroot}%{_mandir}/{fr,it,pl,ru}


# remove some c source files
rm -f %{buildroot}%{_datadir}/vim/%{VIM_SUBDIR}/tools/*.c
rm -f %{buildroot}%{_datadir}/vim/%{VIM_SUBDIR}/macros/maze/*.c
#
# Create ghost files (see vim.conf)
mkdir -p %{buildroot}%{_localstatedir}/run/vi.recover
rm -rf %{buildroot}%{_datadir}/icons/hicolor/48x48/apps

%fdupes -s %{buildroot}%{_datadir}/vim/%{VIM_SUBDIR}/lang
%fdupes -s %{buildroot}%{_datadir}/vim/%{VIM_SUBDIR}/tutor
%fdupes -s %{buildroot}%{_datadir}/vim/%{VIM_SUBDIR}/ftplugin

%post
/usr/sbin/update-alternatives --install \
    /usr/bin/vim        vim  /usr/bin/vim-normal          15


%post enhanced
/usr/sbin/update-alternatives --install \
    /usr/bin/vim        vim  %{_bindir}/vim-enhanced  20


%preun
if [ "$1" = 0 ] ; then
    /usr/sbin/update-alternatives --remove vim /usr//bin/vim-normal
fi


%preun enhanced
if [ "$1" = 0 ] ; then
    /usr/sbin/update-alternatives --remove vim %{_bindir}/vim-enhanced
fi


%docs_package

%files
%manifest %{name}.manifest
%license LICENSE
%defattr(-,root,root,-)
%{_bindir}/vim-normal

%files base
%manifest %{name}.manifest
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/vimrc
%ghost %{_sysconfdir}/alternatives/vim
%{_bindir}/edit
%{_bindir}/ex
%{_bindir}/rview
%{_bindir}/rvim
%{_bindir}/vi
%{_bindir}/vim
%{_bindir}/view
%{_bindir}/vimdiff
# additional binaries
%{_bindir}/vimtutor
%{_bindir}/xxd
# docs and data file
%doc %{_docdir}/vim
#
%{_datadir}/vim/current
%dir %{_datadir}/vim/
%dir %{_datadir}/vim/%{VIM_SUBDIR}/
%dir %{_datadir}/vim/%{VIM_SUBDIR}/autoload/
%dir %{_datadir}/vim/%{VIM_SUBDIR}/colors/
%dir %{_datadir}/vim/%{VIM_SUBDIR}/compiler/
%dir %{_datadir}/vim/%{VIM_SUBDIR}/doc/
%dir %{_datadir}/vim/%{VIM_SUBDIR}/ftplugin/
%dir %{_datadir}/vim/%{VIM_SUBDIR}/indent/
%dir %{_datadir}/vim/%{VIM_SUBDIR}/keymap/
%dir %{_datadir}/vim/%{VIM_SUBDIR}/lang/
%dir %{_datadir}/vim/%{VIM_SUBDIR}/macros/
%dir %{_datadir}/vim/%{VIM_SUBDIR}/plugin/
%dir %{_datadir}/vim/%{VIM_SUBDIR}/print/
%dir %{_datadir}/vim/%{VIM_SUBDIR}/spell/
%dir %{_datadir}/vim/%{VIM_SUBDIR}/syntax/
%dir %{_datadir}/vim/%{VIM_SUBDIR}/tools/
%dir %{_datadir}/vim/%{VIM_SUBDIR}/tutor/
%dir %{_datadir}/vim/%{VIM_SUBDIR}/skeletons/
%dir %{site_runtimepath}
%dir %{site_runtimepath}/autoload/
%dir %{site_runtimepath}/colors/
%dir %{site_runtimepath}/doc/
%dir %{site_runtimepath}/plugin/
%dir %{site_runtimepath}/syntax/
%dir %{site_runtimepath}/ftdetect/
%dir %{site_runtimepath}/after/
%dir %{site_runtimepath}/after/syntax/
#
%{_datadir}/vim/%{VIM_SUBDIR}/bugreport.vim
%{_datadir}/vim/%{VIM_SUBDIR}/evim.vim
%{_datadir}/vim/%{VIM_SUBDIR}/filetype.vim
%{_datadir}/vim/%{VIM_SUBDIR}/ftoff.vim
%{_datadir}/vim/%{VIM_SUBDIR}/ftplugin.vim
%{_datadir}/vim/%{VIM_SUBDIR}/ftplugof.vim
%{_datadir}/vim/%{VIM_SUBDIR}/indent.vim
%{_datadir}/vim/%{VIM_SUBDIR}/indoff.vim
%{_datadir}/vim/%{VIM_SUBDIR}/optwin.vim
%{_datadir}/vim/%{VIM_SUBDIR}/scripts.vim
%{_datadir}/vim/%{VIM_SUBDIR}/syntax/syntax.vim

%files data
%manifest %{name}.manifest
%defattr(-,root,root,-)
# data files
%{_datadir}/vim/%{VIM_SUBDIR}/autoload/*
%{_datadir}/vim/%{VIM_SUBDIR}/colors/*
%{_datadir}/vim/%{VIM_SUBDIR}/compiler/*
%{_datadir}/vim/%{VIM_SUBDIR}/doc/*
%{_datadir}/vim/%{VIM_SUBDIR}/ftplugin/*
%{_datadir}/vim/%{VIM_SUBDIR}/indent/*
%{_datadir}/vim/%{VIM_SUBDIR}/keymap/*
%{_datadir}/vim/%{VIM_SUBDIR}/lang/*
%{_datadir}/vim/%{VIM_SUBDIR}/macros/*
%{_datadir}/vim/%{VIM_SUBDIR}/plugin/*
%{_datadir}/vim/%{VIM_SUBDIR}/print/*
%{_datadir}/vim/%{VIM_SUBDIR}/spell/*
%{_datadir}/vim/%{VIM_SUBDIR}/syntax/*
%exclude %{_datadir}/vim/%{VIM_SUBDIR}/syntax/syntax.vim
#%{_datadir}/vim/%{VIM_SUBDIR}/tools/blink.c
%{_datadir}/vim/%{VIM_SUBDIR}/tools/ccfilter.1
#%{_datadir}/vim/%{VIM_SUBDIR}/tools/ccfilter.c
%{_datadir}/vim/%{VIM_SUBDIR}/tools/ccfilter_README.txt
%{_datadir}/vim/%{VIM_SUBDIR}/tools/efm_filter.pl
%{_datadir}/vim/%{VIM_SUBDIR}/tools/efm_filter.txt
%{_datadir}/vim/%{VIM_SUBDIR}/tools/efm_perl.pl
%{_datadir}/vim/%{VIM_SUBDIR}/tools/mve.awk
%{_datadir}/vim/%{VIM_SUBDIR}/tools/mve.txt
%{_datadir}/vim/%{VIM_SUBDIR}/tools/pltags.pl
%{_datadir}/vim/%{VIM_SUBDIR}/tools/README.txt
%{_datadir}/vim/%{VIM_SUBDIR}/tools/ref
%{_datadir}/vim/%{VIM_SUBDIR}/tools/shtags.1
%{_datadir}/vim/%{VIM_SUBDIR}/tools/shtags.pl
%{_datadir}/vim/%{VIM_SUBDIR}/tools/unicode.vim
%{_datadir}/vim/%{VIM_SUBDIR}/tools/vimm
%exclude %{_datadir}/vim/%{VIM_SUBDIR}/tools/vim132
%{_datadir}/vim/%{VIM_SUBDIR}/tools/vimspell.sh
%{_datadir}/vim/%{VIM_SUBDIR}/tools/vimspell.txt
%{_datadir}/vim/%{VIM_SUBDIR}/tools/vim_vs_net.cmd
#%{_datadir}/vim/%{VIM_SUBDIR}/tools/xcmdsrv_client.c
%{_datadir}/vim/%{VIM_SUBDIR}/tutor/*
%{_datadir}/vim/%{VIM_SUBDIR}/delmenu.vim
%{_datadir}/vim/%{VIM_SUBDIR}/menu.vim
%{_datadir}/vim/%{VIM_SUBDIR}/mswin.vim
%{_datadir}/vim/%{VIM_SUBDIR}/synmenu.vim
%{_datadir}/vim/%{VIM_SUBDIR}/gvimrc_example.vim
%{_datadir}/vim/%{VIM_SUBDIR}/vimrc_example.vim

%files enhanced
%manifest %{name}.manifest
%defattr(-,root,root,-)
%{_bindir}/vim-enhanced


%changelog
