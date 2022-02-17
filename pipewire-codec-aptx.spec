%global  meson_config meson _build --prefix=/usr --libdir=%{_libdir} --libexecdir=/usr/libexec --bindir=/usr/bin --sbindir=/usr/sbin --includedir=/usr/include --datadir=/usr/share --mandir=/usr/share/man --infodir=/usr/share/info --localedir=/usr/share/locale --sysconfdir=/etc

%global debug_package %{nil}

%global realname pipewire

%global majorversion 0
%global minorversion 3
%if %{?fedora} >= 35
%global microversion 45
%else 
%global microversion 40
%endif

%global apiversion   0.3
%global spaversion   0.2
%global soversion    0
%global libversion   %{soversion}.%(bash -c '((intversion = (%{minorversion} * 100) + %{microversion})); echo ${intversion}').0

# For rpmdev-bumpspec and releng automation
%global baserelease 7

#global snapdate   20220203
#global gitcommit  bdd407fe66cc9e46d4bc4dcc989d50679000482b
#global shortcommit %(c=%{gitcommit}; echo ${c:0:7})

# https://bugzilla.redhat.com/983606
%global _hardened_build 1

# where/how to apply multilib hacks
%global multilib_archs x86_64 %{ix86} ppc64 ppc s390x s390 sparc64 sparcv9 ppc64le

# Build conditions for various features
%bcond_without alsa
%bcond_without media_session
%bcond_without vulkan

# Features disabled for RHEL 8
%if 0%{?rhel} && 0%{?rhel} < 9
%bcond_with pulse
%bcond_with jack
%else
%bcond_without pulse
%bcond_without jack
%endif

# Features disabled for RHEL
%if 0%{?rhel}
%bcond_with jackserver_plugin
%else
%bcond_without jackserver_plugin
%endif

%if 0%{?rhel} || 0%{?fedora} < 36
%bcond_with libcamera_plugin
%else
%bcond_without libcamera_plugin
%endif

Name:           pipewire-codec-aptx
Summary:        Media Sharing Server
Version:        %{majorversion}.%{minorversion}.%{microversion}
Release:        %{baserelease}%{?snapdate:.%{snapdate}git%{shortcommit}}%{?dist}
License:        MIT
URL:            https://pipewire.org/
%if 0%{?snapdate}
Source0:        https://gitlab.freedesktop.org/pipewire/pipewire/-/archive/%{gitcommit}/pipewire-%{shortcommit}.tar.gz
%else
Source0:        https://gitlab.freedesktop.org/pipewire/pipewire/-/archive/%{version}/pipewire-%{version}.tar.gz
%endif

## upstream patches


## upstreamable patches

## fedora patches

BuildRequires:  gettext
BuildRequires:  meson >= 0.49.0
BuildRequires:  cmake
BuildRequires:  gcc
BuildRequires:  g++
BuildRequires:  pkgconfig
BuildRequires:  pkgconfig(libudev)
BuildRequires:  pkgconfig(dbus-1)
BuildRequires:  pkgconfig(glib-2.0) >= 2.32
BuildRequires:  pkgconfig(gio-unix-2.0) >= 2.32
BuildRequires:  pkgconfig(gstreamer-1.0) >= 1.10.0
BuildRequires:  pkgconfig(gstreamer-base-1.0) >= 1.10.0
BuildRequires:  pkgconfig(gstreamer-plugins-base-1.0) >= 1.10.0
BuildRequires:  pkgconfig(gstreamer-net-1.0) >= 1.10.0
BuildRequires:  pkgconfig(gstreamer-allocators-1.0) >= 1.10.0
# libldac is not built on x390x, see rhbz#1677491
%ifnarch s390x
BuildRequires:  pkgconfig(ldacBT-enc)
BuildRequires:  pkgconfig(ldacBT-abr)
%endif
%if %{with vulkan}
BuildRequires:  pkgconfig(vulkan)
%endif
BuildRequires:  pkgconfig(bluez)
BuildRequires:  systemd-devel >= 184
BuildRequires:  alsa-lib-devel
BuildRequires:  libv4l-devel
BuildRequires:  doxygen
BuildRequires:  python-docutils
BuildRequires:  graphviz
BuildRequires:  sbc-devel
BuildRequires:  libsndfile-devel
BuildRequires:  ncurses-devel
BuildRequires:  pulseaudio-libs-devel
BuildRequires:  avahi-devel
BuildRequires:  pkgconfig(webrtc-audio-processing) >= 0.2
BuildRequires:  libusb-devel
BuildRequires:  libfreeaptx-devel
BuildRequires:  jack-audio-connection-kit-devel
BuildRequires:  fdk-aac-free-devel
BuildRequires:  ffmpeg-devel >= 5.0
BuildRequires:  libcanberra-devel
BuildRequires:  openssl-devel
BuildRequires:  lilv-devel
BuildRequires:  libdrm-devel
BuildRequires:  readline-devel

Requires:       pipewire >= %{version}


%description
PipeWire is a multimedia server for Linux and other Unix like operating
systems.

%package -n pipewire-spa-ffmpeg
Summary: FFmpeg SPA plugin
%description -n pipewire-spa-ffmpeg
Low-latency audio/video router and processor - FFmpeg SPA plugin
Requires:       pipewire >= %{version}


%prep
%autosetup -p1 -n %{realname}-%{version}

%build

	
%meson_config \
    -D docs=enabled -D man=enabled -D gstreamer=enabled -D systemd=enabled	\
    -D gstreamer-device-provider=disabled -D sdl2=disabled 			\
    -D audiotestsrc=disabled -D videotestsrc=disabled				\
    -D volume=disabled -D bluez5-codec-aptx=disabled -D roc=disabled 		\
    -D ffmpeg=enabled -D bluez5-codec-aptx=enabled 				\
%ifarch s390x
    -D bluez5-codec-ldac=disabled						\
%endif
    %{!?with_media_session:-D session-managers=[]} 				\
    %{!?with_jack:-D pipewire-jack=disabled} 					\
    %{!?with_jackserver_plugin:-D jack=disabled} 				\
    %{!?with_libcamera_plugin:-D libcamera=disabled} 				\
    %{?with_jack:-D jack-devel=true} 					\
    %{!?with_alsa:-D pipewire-alsa=disabled}					\
    %{?with_vulkan:-D vulkan=enabled}
%meson_build -C _build



%install
install -dm 755 %{buildroot}%{_libdir}/spa-%{spaversion}/bluez5 
install -dm 755 %{buildroot}/%{_libdir}/spa-%{spaversion}/ffmpeg

install -m644  _build/spa/plugins/bluez5/libspa-codec-bluez5-aptx.so %{buildroot}%{_libdir}/spa-%{spaversion}/bluez5/
install -m644  _build/spa/plugins/ffmpeg/libspa-ffmpeg.so %{buildroot}/%{_libdir}/spa-%{spaversion}/ffmpeg/

%files
%license COPYING
%{_libdir}/spa-*/bluez5/libspa-codec-bluez5-aptx.so

%files -n pipewire-spa-ffmpeg
%license COPYING
%{_libdir}/spa-*/ffmpeg/libspa-ffmpeg.so

%changelog

* Sun Feb 13 2022 Unitedrpms Project <unitedrpms AT protonmail DOT com> - 0.3.47-7
- Updated to 0.3.47-7

* Fri Sep 24 2021 Unitedrpms Project <unitedrpms AT protonmail DOT com> - 0.3.37-7
- Used the base rpm for our subpackages
- Initial build

* Thu Sep 23 2021 Javier Martinez Canillas <javierm@redhat.com> - 0.3.37-2
- Enable libcamera SPA plugin
