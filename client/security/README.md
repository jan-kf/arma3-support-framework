# Steam container security profiles

`pontifex-steam-seccomp.json` is derived from Moby's official
[`seccomp/v0.2.1`](https://github.com/moby/profiles/blob/seccomp/v0.2.1/seccomp/default.json)
profile (source SHA-256
`536529b665dd0972c37bfb569f5d4ac8a53592e7b00752bc39ff063ca9864c74`).
That profile is Docker's documented compatibility profile for i386/Steam and
retains the AF_ALG socket restriction. Pontifex adds only:

- `unshare`, `mount`, `pivot_root`, `umount2`, and `chroot`, whose privileged
  uses remain blocked by the kernel because the client has no capabilities in
  its initial user namespace;
- `clone(2)` namespace combinations used by Steam's bubblewrap and Chromium
  sandboxes. With every container capability dropped, the kernel rejects
  privileged namespace combinations unless they create or are already inside
  an unprivileged user namespace.

`pontifex-steam.apparmor` is derived from Moby's
[`docker-default` AppArmor template](https://github.com/moby/profiles/blob/master/apparmor/template.go).
It replaces the blanket mount denial with mount, unmount, and
pivot-root permissions needed inside bubblewrap's nested user namespace while
retaining Docker's procfs, sysfs, AF_ALG, signal, and ptrace restrictions.

The long-lived Steam client still drops every Linux capability and uses
`no-new-privileges`. Only a short-lived, read-only, networkless setup container
loads the named AppArmor policy into the host kernel. Pontifex then fails closed
unless a confined bubblewrap probe succeeds.
