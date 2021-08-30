# Perfetto Binaries

The source code for several perfetto binaries lives in the `external/perfetto`
project in the AOSP source tree. These  binaries enable unbundled perfetto
tracing, and on-device trace processing.

To set up the perfetto repository for the first time:

```bash
git clone https://android.googlesource.com/platform/external/perfetto/ perfetto_repo
perfetto_repo/tools/install-build-deps --android
```

To build stripped binaries from the local repository:

```bash
./generate_perfetto_binaries.py
```

This script automates some of the build instructions documented
[here](https://perfetto.dev/docs/contributing/build-instructions).

Some important things handled are:
 - binary stripping (drastically reduces binary size)
 - sets `monolithic_binaries = true` (important for unbundled usage)
 - handles all architectures supported by macrobenchmark
