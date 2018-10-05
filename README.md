# travis-compact-status

Shows a compact report of recent builds and branches in the given
repository on Travis CI.

```
$ travis-compact-status builds
PPPPPPPPP  jm/svn-pushmergeinfo-fix
XXXXXPXPP  pb/bisect-helper-2
PPPPPPPPP  bw/oidmap-autoinit
PPPPPPPPX  nd/diff-flush-before-warning
PPPPPPPPP  jh/partial-clone
PPPPPPPPP  jk/abort-clone-with-existing-dest
```

Each letter on the left represents the status of a build job of the
branch on the right.  The meaning of letters is as follows:

```
c - Created
q - Queued
b - Received
s - Started
P - Passed
! - Errored
X - Failed
_ - Canceled
```
