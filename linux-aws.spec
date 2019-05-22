#
# This is a special configuration of the Linux kernel, based on linux package
# for AWS support
#

Name:           linux-aws
Version:        5.0.18
Release:        123
License:        GPL-2.0
Summary:        The Linux kernel for use in the AWS cloud
Url:            http://www.kernel.org/
Group:          kernel
Source0:        https://cdn.kernel.org/pub/linux/kernel/v5.x/linux-5.0.18.tar.xz
Source1:        config
Source2:        cmdline

%define ktarget  aws
%define kversion %{version}-%{release}.%{ktarget}

BuildRequires:  buildreq-kernel

Requires: systemd-bin
Requires: init-rdahead
Requires: %{name}-license = %{version}-%{release}

# don't strip .ko files!
%global __os_install_post %{nil}
%define debug_package %{nil}
%define __strip /bin/true

#    000X: cve, bugfixes patches
Patch0001: CVE-2019-9500.patch
Patch0002: CVE-2019-9503.patch

#    00XY: Mainline patches, upstream backports

#Serie.clr 01XX: Clear Linux patches
Patch0101: 0101-i8042-decrease-debug-message-level-to-info.patch
Patch0102: 0102-Increase-the-ext4-default-commit-age.patch
Patch0103: 0103-pci-pme-wakeups.patch
Patch0104: 0104-ksm-wakeups.patch
Patch0105: 0105-xattr-allow-setting-user.-attributes-on-symlinks-by-.patch
Patch0106: 0106-init_task-faster-timerslack.patch
Patch0107: 0107-overload-on-wakeup.patch
Patch0108: 0108-smpboot-reuse-timer-calibration.patch
Patch0109: 0109-raid6-add-Kconfig-option-to-skip-raid6-benchmarking.patch
Patch0110: 0110-reduce-e1000e-boot-time-by-tightening-sleep-ranges.patch
Patch0111: 0111-give-rdrand-some-credit.patch
Patch0112: 0112-e1000e-change-default-policy.patch
Patch0113: 0113-ipv4-tcp-tuning-memory.patch
Patch0114: 0114-tweak-perfbias.patch
Patch0115: 0115-xen-xenbus-don-t-be-slow.patch
Patch0116: 0116-xen-blkfront-small-tunning-for-block-dev.patch
Patch0117: 0117-time-ntp-fix-wakeups.patch
Patch0118: 0118-mm-reduce-vmstat-wakups.patch
Patch0119: 0119-config-no-Atom.patch
Patch0120: 0120-acpi-cache-ADR.patch
Patch0121: 0121-acpi-status-cache.patch
Patch0122: 0122-init-wait-for-partition-and-retry-scan.patch
Patch0123: 0123-ena-async.patch
Patch0124: 0124-nvme-decrease-msleep.patch
Patch0125: 0125-Migrate-some-systemd-defaults-to-the-kernel-defaults.patch
Patch0126: 0126-use-lfence-instead-of-rep-and-nop.patch
Patch0127: 0127-do-accept-in-LIFO-order-for-cache-efficiency.patch
Patch0128: 0128-zero-extra-registers.patch
Patch0129: 0129-locking-rwsem-spin-faster.patch
#Serie.clr.end

#Serie1.name WireGuard
#Serie1.git  https://git.zx2c4.com/WireGuard
#Serie1.cmt  91b0a211861d487382a534572844ff29839064f1
#Serie1.tag  0.0.20190406
Patch1001: 1001-WireGuard-fast-modern-secure-kernel-VPN-tunnel.patch
#Serie1.end

%description
The Linux kernel.

%package extra
License:        GPL-2.0
Summary:        The Linux kernel extra files
Group:          kernel
Requires:       %{name}-license = %{version}-%{release}

%description extra
Linux kernel extra files

%package license
Summary: license components for the linux package.
Group: Default

%description license
license components for the linux package.

%prep
%setup -q -n linux-5.0.18

#     000X  cve, bugfixes patches
%patch0001 -p1
%patch0002 -p1

#     00XY  Mainline patches, upstream backports

#     01XX  Clear Linux patches
%patch0101 -p1
%patch0102 -p1
%patch0103 -p1
%patch0104 -p1
%patch0105 -p1
%patch0106 -p1
%patch0107 -p1
%patch0108 -p1
%patch0109 -p1
%patch0110 -p1
%patch0111 -p1
%patch0112 -p1
%patch0113 -p1
%patch0114 -p1
%patch0115 -p1
%patch0116 -p1
%patch0117 -p1
%patch0118 -p1
%patch0119 -p1
%patch0120 -p1
%patch0121 -p1
%patch0122 -p1
%patch0123 -p1
%patch0124 -p1
%patch0125 -p1
%patch0126 -p1
%patch0127 -p1
%patch0128 -p1
%patch0129 -p1

#Serie1.patch.start
%patch1001 -p1
#Serie1.patch.end

cp %{SOURCE1} .

%build
BuildKernel() {

    Target=$1
    Arch=x86_64
    ExtraVer="-%{release}.${Target}"

    perl -p -i -e "s/^EXTRAVERSION.*/EXTRAVERSION = ${ExtraVer}/" Makefile

    make O=${Target} -s mrproper
    cp config ${Target}/.config

    make O=${Target} -s ARCH=${Arch} olddefconfig
    make O=${Target} -s ARCH=${Arch} CONFIG_DEBUG_SECTION_MISMATCH=y %{?_smp_mflags} %{?sparse_mflags}
}

BuildKernel %{ktarget}

%install

InstallKernel() {

    Target=$1
    Kversion=$2
    Arch=x86_64
    KernelDir=%{buildroot}/usr/lib/kernel

    mkdir   -p ${KernelDir}
    install -m 644 ${Target}/.config    ${KernelDir}/config-${Kversion}
    install -m 644 ${Target}/System.map ${KernelDir}/System.map-${Kversion}
    install -m 644 ${Target}/vmlinux    ${KernelDir}/vmlinux-${Kversion}
    install -m 644 %{SOURCE2}           ${KernelDir}/cmdline-${Kversion}
    cp  ${Target}/arch/x86/boot/bzImage ${KernelDir}/org.clearlinux.${Target}.%{version}-%{release}
    chmod 755 ${KernelDir}/org.clearlinux.${Target}.%{version}-%{release}

    mkdir -p %{buildroot}/usr/lib/modules
    make O=${Target} -s ARCH=${Arch} INSTALL_MOD_PATH=%{buildroot}/usr modules_install

    rm -f %{buildroot}/usr/lib/modules/${Kversion}/build
    rm -f %{buildroot}/usr/lib/modules/${Kversion}/source

    # Kernel default target link
    ln -s org.clearlinux.${Target}.%{version}-%{release} %{buildroot}/usr/lib/kernel/default-${Target}
}

InstallKernel %{ktarget} %{kversion}

rm -rf %{buildroot}/usr/lib/firmware

mkdir -p %{buildroot}/usr/share/package-licenses/linux-aws
cp COPYING %{buildroot}/usr/share/package-licenses/linux-aws/COPYING
cp -a LICENSES/* %{buildroot}/usr/share/package-licenses/linux-aws

%files
%dir /usr/lib/kernel
%dir /usr/lib/modules/%{kversion}
/usr/lib/kernel/config-%{kversion}
/usr/lib/kernel/cmdline-%{kversion}
/usr/lib/kernel/org.clearlinux.%{ktarget}.%{version}-%{release}
/usr/lib/kernel/default-%{ktarget}
/usr/lib/modules/%{kversion}/kernel
/usr/lib/modules/%{kversion}/modules.*

%files extra
%dir /usr/lib/kernel
/usr/lib/kernel/System.map-%{kversion}
/usr/lib/kernel/vmlinux-%{kversion}

%files license
%defattr(0644,root,root,0755)
/usr/share/package-licenses/linux-aws
